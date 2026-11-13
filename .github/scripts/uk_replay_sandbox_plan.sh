# Pure command and transition planning shared by the executor and data-only tests.
# Definitions only: no command is run and no shell option is changed on source.
sandbox_plan_reset() {
  PLAN_ARGV=() PLAN_ACTION= PLAN_NEXT= PLAN_COUNT=0 PLAN_STDIN= PLAN_ERROR= PLAN_STATUS=0
}

sandbox_argv() {
  sandbox_plan_reset
  local target=$1 home=$2 offline=() settings=()
  shift 2
  if [ "${1:-}" = --offline ]; then
    offline=(-p PrivateNetwork=yes -p RestrictAddressFamilies=AF_INET
      -p RestrictAddressFamilies=AF_INET6 -p RestrictAddressFamilies=AF_NETLINK
      -p SystemCallArchitectures=native
      -p "SystemCallFilter=~io_uring_setup io_uring_enter io_uring_register"
      -p SystemCallErrorNumber=EPERM)
    shift
  fi
  while [ "$#" -gt 0 ] && [[ "$1" == *=* ]]; do
    settings+=(--setenv "$1")
    shift
  done
  PLAN_ARGV=(sudo systemd-run --quiet --collect --pipe --wait
    --uid="$target" --gid="$target" --working-directory="$home"
    --setenv HOME="$home" --setenv USER="$target" --setenv LANG=C.UTF-8
    --setenv PATH="$home/bin:/usr/local/bin:/usr/bin:/bin"
    ${settings[@]+"${settings[@]}"}
    -p ProtectSystem=strict -p ReadWritePaths="$home"
    -p InaccessiblePaths=-/home/runner -p PrivateTmp=yes -p PrivateDevices=yes
    -p NoNewPrivileges=yes -p RestrictSUIDSGID=yes -p ProtectProc=invisible
    -p ProtectKernelTunables=yes -p ProtectKernelModules=yes -p ProtectKernelLogs=yes
    -p ProtectClock=yes -p ProtectControlGroups=yes -p RestrictNamespaces=yes
    -p LockPersonality=yes -p CapabilityBoundingSet= ${offline[@]+"${offline[@]}"} "$@")
  PLAN_ACTION=command
}

# Each probe's observation is supplied by the executor, not looked up here.
# A negative poll still goes through the independent final probe.
stop_next() {
  sandbox_plan_reset
  local state=$1 observed=$2 count=$3 target=$4
  case "$count" in [0-9]|[12][0-9]|30) ;; *) PLAN_ACTION=refuse; PLAN_ERROR='invalid poll count'; PLAN_STATUS=2; return ;; esac
  PLAN_COUNT=$count
  case "$state" in
    kill) PLAN_ACTION=kill; PLAN_NEXT=poll; PLAN_ARGV=(sudo pkill -KILL -u "$target") ;;
    poll) PLAN_ACTION=probe; PLAN_NEXT=polled; PLAN_ARGV=(pgrep -u "$target") ;;
    polled)
      case "$observed" in
        absent) PLAN_ACTION=advance; PLAN_NEXT=verify ;;
        present)
          if [ "$count" -ge 30 ]; then
            PLAN_ACTION=refuse; PLAN_ERROR='poll limit exceeded'; PLAN_STATUS=2
          else
            PLAN_ACTION=sleep; PLAN_ARGV=(sleep 1); PLAN_COUNT=$((count + 1))
            if [ "$PLAN_COUNT" -eq 30 ]; then PLAN_NEXT=verify; else PLAN_NEXT=poll; fi
          fi ;;
        *) PLAN_ACTION=refuse; PLAN_ERROR='invalid process observation'; PLAN_STATUS=2 ;;
      esac ;;
    verify) PLAN_ACTION=probe; PLAN_NEXT=verified; PLAN_ARGV=(pgrep -u "$target") ;;
    verified)
      case "$observed" in
        absent) PLAN_ACTION=done ;;
        present) PLAN_ACTION=refuse; PLAN_ERROR="$target processes survive"; PLAN_STATUS=1 ;;
        *) PLAN_ACTION=refuse; PLAN_ERROR='invalid process observation'; PLAN_STATUS=2 ;;
      esac ;;
    *) PLAN_ACTION=refuse; PLAN_ERROR='invalid stop state'; PLAN_STATUS=2 ;;
  esac
}

# Replay's executor supplies settings and the preceding hand-in's real status.
replay_next() {
  sandbox_plan_reset
  local state=$1 observed=$2 target=$3 home=$4 dataset=$5 variant=$6 event=$7 measure=$8 year=$9
  local values=("$dataset" "$variant" "$event" "$measure" "$year")
  local names=(DATASET_FILE VARIANT REPLAY_EVENT REPLAY_MEASURE REPLAY_YEAR) i
  for i in 0 1 2 3 4; do
    if [ -z "${values[$i]}" ]; then
      PLAN_ACTION=refuse; PLAN_ERROR=${names[$i]}; PLAN_STATUS=1; return
    fi
  done
  case "$state" in
    start) PLAN_ACTION=stop; PLAN_NEXT=handin ;;
    handin)
      sandbox_argv "$target" "$home" --offline /bin/sh -c \
        '/bin/rm -rf "$HOME/scorecard/input" && /bin/mkdir "$HOME/scorecard/input" && exec /bin/cat > "$HOME/scorecard/input/dataset.h5"'
      PLAN_ACTION=handin; PLAN_NEXT=handed; PLAN_STDIN=$dataset ;;
    handed)
      if [ "$observed" = 0 ]; then
        PLAN_ACTION=advance; PLAN_NEXT=replay
      else
        PLAN_ACTION=refuse; PLAN_STATUS=$observed; PLAN_ERROR='dataset hand-in failed'
      fi ;;
    replay)
      sandbox_argv "$target" "$home" --offline PYTHONPATH=. \
        VARIANT="$variant" REPLAY_EVENT="$event" REPLAY_MEASURE="$measure" REPLAY_YEAR="$year" \
        /bin/bash -c 'cd "$HOME/scorecard" && exec bash .github/scripts/uk_replay_determinism.sh replay'
      PLAN_ACTION=replay; PLAN_NEXT=done ;;
    done) PLAN_ACTION=done ;;
    *) PLAN_ACTION=refuse; PLAN_ERROR='invalid replay state'; PLAN_STATUS=2 ;;
  esac
}

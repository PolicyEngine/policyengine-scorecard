# Definitions only. Tests use these same IO primitives with benign owned sinks.
sandbox_stream_dataset() {
  local dataset=$1
  shift
  /bin/cat "$dataset" | "$@"
}

# Run a command whose output the variant writes, with the runner's workflow
# commands stopped until a token the variant never sees. Its stderr joins
# stdout: the runner reads stderr as a second stream, where a last line
# without a newline would reach it only after the token. setup-uv registers
# a problem matcher (owner python) for the rest of the job, and matchers
# read plain lines, which stopping commands does not stop, so it goes first.
untrusted_output() {
  local token status=0
  token=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  echo "::remove-matcher owner=python::"
  echo "::stop-commands::$token"
  "$@" 2>&1 || status=$?
  printf '\n::%s::\n' "$token"
  return "$status"
}

#!/bin/env sh

check_service() {
  # The first argument is the URL to check.
  local url="$1"

  # Check if a URL was provided.
  if [ -z "$url" ]; then
    echo "Error: No URL provided." >&2
    return 1
  fi

  # Use curl to perform a quick check.
  # -s: Silent mode. Hides progress meter and error messages.
  # -o /dev/null: Discards the output. We only care about the exit code.
  # -I: Fetches only the HTTP headers. Faster than downloading the full body.
  # -L: Follows redirects.
  # --connect-timeout 5: Fails after 5 seconds if a connection cannot be established.
  # --write-out '%{http_code}': Prints the HTTP status code.
  http_code=$(curl -X GET -s -o /dev/null -I -L --connect-timeout 5 --write-out '%{http_code}' "$url")
  
  # Check the exit code of curl. A non-zero exit code means an error occurred.
  local curl_exit_code=$?
  if [ $curl_exit_code -ne 0 ]; then
    echo "Service at $url is inaccessible. Curl exit code: $curl_exit_code"
    return 1
  fi

  # Check if the HTTP status code indicates success (2xx or 3xx).
  if echo "$http_code" | grep -E -q '^(2|3)[0-9]{2}$'; then
    echo "Success: Service at $url is accessible. Status code: $http_code"
    return 0
  else
    echo "Warning: Service at $url returned a non-success status code: $http_code"
    return 1
  fi
}
# TLS Troubleshooting Runbook

Commands for diagnosing the four most common TLS failures on the
operations gateway. All commands assume you run them from a machine
that can reach `localhost:8443`.

## Failure 1 — Certificate expired

Symptom: browsers and curl report "certificate has expired" and
connections fail during the TLS handshake.

Diagnose:

    openssl s_client -connect localhost:8443 -servername localhost 2>&1 | \
      openssl x509 -noout -dates

    Expected output shows notBefore and notAfter dates.

Check whether the current date is past notAfter:

    date

If expired, the fix is to regenerate the certificate. Reference: the
openssl x509 documentation covers the -dates flag.

    cd ~/NGINX-GLOBAL-OPERATIONS-HUB/01-MANAGEMENT/37-public-data-gateway/certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout gateway.key -out gateway.crt \
      -subj "//C=ZA\ST=Gauteng\L=Johannesburg\O=Ops\CN=localhost"
    docker restart nginx-public-data-gateway

## Failure 2 — Certificate and key do not match

Symptom: nginx refuses to start with "cannot load certificate" or
"key values mismatch".

Diagnose:

    openssl x509 -noout -modulus -in gateway.crt | openssl md5
    openssl rsa  -noout -modulus -in gateway.key | openssl md5

The two md5 hashes must match. If they don't, the key does not
correspond to the certificate. Reference: openssl x509 and openssl
rsa man pages, modulus and md5 output flags.

Fix: regenerate both together — a mismatched pair cannot be
repaired individually.

## Failure 3 — TLS version mismatch

Symptom: "no protocols available" or "unsupported protocol" when
a client tries to connect.

Diagnose:

    openssl s_client -connect localhost:8443 -tls1_1

If the server has ssl_protocols set to "TLSv1.2 TLSv1.3" (which is
the current config), the output will end with "no protocols
available". That is the correct behaviour. Reference: the
ssl_protocols directive in ngx_http_ssl_module.

If you need to support older clients temporarily, add the protocol
back to nginx.conf and reload:

    sed -i 's/ssl_protocols TLSv1.2 TLSv1.3;/ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;/' nginx.conf
    docker restart nginx-public-data-gateway

## Failure 4 — Cipher mismatch

Symptom: "no shared cipher" or "handshake failure" with older
clients.

Diagnose:

    openssl s_client -connect localhost:8443 -cipher 'RC4-SHA'

If the server's ssl_ciphers list only allows modern ECDHE-GCM
suites (which is the current config), the output will end with
"no cipher match". That is the correct behaviour.

To see which ciphers the server actually offers:

    openssl s_client -connect localhost:8443 -cipher 'ALL'

Reference: the ssl_ciphers directive in ngx_http_ssl_module, and
the openssl ciphers command.

## Diagnosing mTLS failures

Symptom: client with certificate still gets rejected, or client
without certificate gets "400 No required SSL certificate was sent".

Diagnose:

    curl -v --cert client.crt --key client.key https://localhost:8443/

Verbose output shows the TLS handshake. Look for these lines:

    SSL connection using TLSv1.3
    Server certificate: ...  (should match CN of gateway.crt)
    Client certificate: ...  (should match CN of client.crt)

If the client cert is not presented, curl logs "schannel: disabled
automatic use of client certificate" — this is a Windows schannel
limitation. Use WSL, Linux, or macOS curl to test mTLS. Reference:
curl docs --cert flag, and the schannel-specific limitations
documented in curl's Windows section.

## General diagnostic command

The one command that shows everything at once:

    curl -v -k https://localhost:8443/health 2>&1 | head -30

The verbose output includes the TLS version, cipher suite, server
certificate chain, and any handshake errors. This is the first thing
to run when TLS is misbehaving.

## References

- openssl s_client man page: https://www.openssl.org/docs/man1.1.1/man1/s_client.html
- ngx_http_ssl_module: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
- curl --cert option: https://curl.se/docs/manpage.html#-E
- F5 NGINX certification blueprint Exam 4.3: TLS troubleshooting

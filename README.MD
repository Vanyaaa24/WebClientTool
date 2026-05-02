#Assignment 1

WebTester is a Pyhton based web client tool that analyzes web servers by sending HTTP requests and examining responses. It extracts information about
-HTTP/2 protocol support
-Cookies
-Password protection status
-Automatically follows HTTP redirects

How to Run:
Command:
    pyhton3 WebTester.py <URL>
Example <URL's>
-----www.uvic.ca------
-----hhtps://www.uvic.ca----
----www.google.ca---
---thisdoesnotexist.com---
---https://httpbin.org/basic-auth/myuser/mypass----

#Features Implemented

##HTTP/2 Support Detection
HTTP/2 support is detected using TLS ALPN negotiation
The program detects HTTP/2 capability without changing the HTTP request syntax
all requests are still sent using HTTP/1.1 as reqd. by the assignment

Known Behavior:
Some servers (e.g., httpbin.org) primarily serve content over HTTP/2 and may
not return a readable HTTP/1.1 response after ALPN negotiation.
In such cases, HTTP/2 support is still correctly detected, but response
parsing may be limited by server behavior.


##Cookies Hnadling
Cookies are extracted manually from Set-coookie header
Cookie name, domain name, expiry date are parsed correctly
No external cookie libraries are used

#Password Detection
Pgaes returning 4.0 unauthorised or authentication headers are detected as password-protected
The presence of WWW-authenticate header is lao used to identify protected pages.

##Redirect handling
HTTP status code 301 and/or 302 are handled automaticlaly
The program follows redirects until the final destination is reached.
No redirect limit as per assignment requirements


##Notes:
All the assignment requirements are met
The program is built using python3 and following socket programming
Different function are created to increase the readability of the program.



##Testing:
The code has been tested on linux server and performs as expected.
Behavior matches expected outputs for valid, invalid, redirected, and protected URLs

###IMPORTANT###
Verbose connection and response output is printed to demonstrate clear undesrtanding of connection and debugging clarity, in addition to all other additional requirements.



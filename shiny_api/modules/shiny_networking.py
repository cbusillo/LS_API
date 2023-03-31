"""Module with useful netowrking functions"""
import subprocess
import paramiko


def is_host_available(host: str) -> bool:
    """Test if ping is successful"""
    command = ["ping", "-c", "1", host]
    try:
        response = subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True, timeout=2
        )
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False
    if "1 packets received" in response:
        return True
    return False


def scp_file_from_host(hostname: str, filename: str) -> bytes:
    """Get file from remote.  Must have keys set up."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, port="2222")
        # Read remote file contents as binary data
        sftp = ssh.open_sftp()

        # execute acl command to grant access to user on file
        acl_command = f"sudo chmod +a 'cbusillo allow read,write,execute' '{filename}'"
        ssh.exec_command(acl_command)

        remote_file = sftp.open(filename, mode="rb")
        file_contents = remote_file.read()
        remote_file.close()
        sftp.close()

        return file_contents

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your username and password.")
    except paramiko.SSHException as ssh_error:
        print(f"SSH error: {ssh_error}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    print(scp_file_from_host("store1.logi.wiki", ""))

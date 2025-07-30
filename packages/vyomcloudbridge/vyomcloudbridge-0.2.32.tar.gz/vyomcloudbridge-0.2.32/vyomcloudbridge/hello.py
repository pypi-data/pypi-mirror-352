import os
import pwd

def setup_ssh_service(ssh_key, ros_username):
    """
    Create and start the ssh service

    Returns:

    """
    print("\n--- Setting ssh service ---")

    # TODO
    # OPEN and save ssh_key in, in home directory of ros_username, ~/.ssh/vyom_gcp_key

    needs_sudo = os.geteuid() != 0
    if needs_sudo:
        print("Error - Root permission required.")
        return False, "Root permission required."
    try:
        user_home = os.path.expanduser(f"~{ros_username}")
        ssh_dir = os.path.join(user_home, ".ssh")
        key_file_path = os.path.join(ssh_dir, "vyom_gcp_key")

        # Ensure .ssh directory exists
        os.makedirs(ssh_dir, mode=0o700, exist_ok=True)

        # Write the ssh_key content to the key file
        with open(key_file_path, "w") as key_file:
            key_file.write(ssh_key)
        os.chmod(key_file_path, 0o600)

        user_info = pwd.getpwnam(ros_username)
        uid = user_info.pw_uid
        gid = user_info.pw_gid
        os.chown(ssh_dir, uid, gid)
        os.chown(key_file_path, uid, gid)
    except Exception as e:
        print("error in prinint the error-",{e})


if __name__ == "__main__":
    ssh_key = """-----BEGIN OPENSSH PRIVATE KEY-----
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
6tQCjg8fIulxEAAAADamV0
-----END OPENSSH PRIVATE KEY-----
"""
    setup_ssh_service(ssh_key, "shitiz")

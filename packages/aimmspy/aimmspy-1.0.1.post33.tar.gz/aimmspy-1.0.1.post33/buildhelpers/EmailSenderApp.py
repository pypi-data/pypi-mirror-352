import argparse
import json
import os
import re

# third party imports
import gitlab
# internal imports
from EmailSender import EmailSender
from internal.gitinfo import gitinfo
from jinja2 import Environment, FileSystemLoader


def get_members_emails(group, gl):
    """
    Retrieve the public email addresses of all members in a given group, excluding those with usernames starting with 'sa_'.

    Args:
        group: The group object containing the members.
        gl: The GitLab instance to fetch user details.

    Returns:
        list: A list of public email addresses of the group members.
    """
    emails = []
    members = group.members.list(all=True)
    for member in members:
        if re.match(r"^sa_", member.username):
            continue
        user = gl.users.get(member.id)
        emails.append(user.public_email)
    return emails


# Function to get group members' email addresses from GitLab
def get_group_emails(gitlab_url, root_group_id, private_token):
    """
    Retrieve email addresses of members from specific GitLab groups.

    This function fetches email addresses of members from a root group and a 
    subgroup in GitLab. The subgroup is determined based on the environment 
    variable 'CI_PROJECT_NAME'.

    Args:
        gitlab_url (str): The URL of the GitLab instance.
        private_token (str): The private token for authenticating with the GitLab API.

    Returns:
        list: A list of unique email addresses of the group members.
    """
    emails = []
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    # Root group: release_notification
    root_group = gl.groups.get(root_group_id)
    emails = get_members_emails(root_group, gl)
    group_name = f"release_notification/{get_env_var('CI_PROJECT_NAME')}".lower(
    )
    for group in gl.groups.list(search=group_name):
        if group.full_path.lower() == group_name:
            group_id = group.id
            break
    group = gl.groups.get(group_id)
    emails.extend(get_members_emails(group, gl))
    # remove duplicates
    emails = list(set(emails))
    return emails


def lookup_default_value(var):
    """
    Lookup the default value for an environment variable based on the CI_PROJECT_NAME.

    Args:
        var (str): The name of the environment variable.

    Returns:
        str: The default value of the environment variable.
    """
    ci_project_name = os.getenv('CI_PROJECT_NAME')
    if ci_project_name is None:
        raise Exception("Environment variable CI_PROJECT_NAME is not set")

    ci_project_name = ci_project_name.lower()
    default_values = {}
    with open(os.path.join(os.path.dirname(__file__), '_default_values.json')) as f:
        default_values = json.load(f)

    project_defaults = default_values.get(ci_project_name, {})
    return project_defaults.get(var, None)


def get_env_var(var_name):
    """
    Retrieve the value of an environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable.

    Raises:
        Exception: If the environment variable is not set.
    """
    value = os.getenv(var_name)
    if value is None:
        try:
            value = lookup_default_value(var_name)
        except Exception as e:
            raise Exception(f"Environment variable {var_name} is not set")
    return value


def get_body(gi, email_body_file):
    """
    Generates the email body by rendering a Jinja2 template.

    Args:
        gi (dict): A dictionary containing data to be passed to the template.
        email_body_file (str): The file path to the Jinja2 template file.

    Returns:
        str: The rendered email body.

    Raises:
        Exception: If the rendered email body is None.
    """
    # Set up the Jinja2 environment
    file_loader = FileSystemLoader(os.path.dirname(email_body_file))
    env = Environment(loader=file_loader)
    template = env.get_template(os.path.basename(email_body_file))
    body = template.render(env=os.environ, gi=gi, get_env_var=get_env_var)
    if body is None:
        raise Exception("Email body is None")
    return body


def main():
    """
    Main function to send an email based on the provided arguments.

    This function parses command-line arguments to determine the email body file,
    whether to perform a dry run, and whether to send a test email. It retrieves
    git information to get the current branch name and version. If the branch is
    not 'master' or 'main', it raises an exception and does not send the email.
    Otherwise, it constructs the email subject and body, and sends the email to
    the appropriate recipients.

    Command-line Arguments:
        --email_body_file (str): Path to the email body Jinja file. Defaults to 'email_body.jinja' in the current directory.
        --dry (bool): Dry run flag. If set, the email will not be sent. Defaults to False.
        --test (bool): Test email flag. If set, the email subject will be prefixed with '[TESTING]'. Defaults to False.

    Raises:
        Exception: If the branch is not 'master' or 'main'.
    """
    parser = argparse.ArgumentParser(description='Send email')
    parser.add_argument('--email_body_file', type=str, help='Path to email body jinja file',
                        default=os.path.join(os.path.dirname(__file__), 'email_body.jinja'))
    parser.add_argument('--dry', action='store_true',
                        help='Dry run flag', default=False)
    parser.add_argument('--test', action='store_true',
                        help='Test email flag', default=False)
    args = parser.parse_args()

    # # check if the path is valid
    # if args.email_body_file is not None:
    #     if not os.path.exists(args.email_body_file):
    #         raise Exception(
    #             f"Email body file {args.email_body_file} does not exist")

    # retrieve git info for the current repo to get the version
    gi = gitinfo()

    print(gi.getFullBranchName())
    print(gi.getVersion())

    # if branch is not master or main, do not send email
    if gi.getFullBranchName() != "master" and gi.getFullBranchName() != "main":
        raise Exception("Not on master or main branch, not sending email")

    subject = f"New Release of {get_env_var('CI_PROJECT_NAME')} Version {gi.getDotVersion()}"
    if args.test:
        subject = f"[TESTING] New Release of {get_env_var('CI_PROJECT_NAME')} Version {gi.getDotVersion()}"
    body = get_body(gi, args.email_body_file)

    print(f"Subject: {subject}")
    print(f"Body: {body}")

    email_sender = EmailSender(
        from_email="general@aimms.com",
    )

    '''
    Send a test email
    run the email server in terminal before running this
    python -m smtpd -c DebuggingServer -n localhost:1025
    test localhost email server
    '''
    # email_sender.test_send_email("Test Subject", "This is a test email body", ["test2@aimms.com", "test3@aimms.com"])

    # the Csaba test csaba.berta@aimms.com
    if not args.dry:
        gitlab_url = get_env_var('CI_SERVER_URL')
        root_group_id = get_env_var('NOTIFICATION_GITLAB_GROUP_ID')
        private_token = get_env_var('NOTIFICATION_GITLAB_PRIVATE_TOKEN')
        emails = get_group_emails(gitlab_url, root_group_id, private_token)
        email_sender.send_aimms_email(subject, body, emails)


if __name__ == "__main__":
    main()

'''
ENVIRONMENT VARIABLES
    CI_SERVER_URL
    NOTIFICATION_GITLAB_GROUP_ID
    NOTIFICATION_GITLAB_PRIVATE_TOKEN
    CI_PROJECT_NAME
    RELEASE_NOTES_WEBSITE_URL
'''

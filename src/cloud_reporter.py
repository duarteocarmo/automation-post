import subprocess
import sys
import papermill as papermill


REMOTE_FOLDER = "your cloud folder name"
LOCAL_FOLDER = "your local folder name"
TEMPLATE_NOTEBOOK = "template_notebook.ipynb"


def get_new_files(remote_folder, local_folder):
    """
    A function that returns files that were uploaded to the cloud folder and 
    do not exist in our local folder. 
    """
    # list the files in our cloud folder
    list_cloud = subprocess.run(
        ["rclone", "lsf", f"remote:{remote_folder}"],
        capture_output=True,
        text=True,
    )

    # transform the command output into a list
    cloud_directories = list_cloud.split("\n")[0:-1]

    print(f"In the cloud we have: \n{cloud_directories}")

    # list the files in our local folder
    list_cloud = subprocess.run(
        ["ls", local_folder], capture_output=True, text=True
    )

    # transform the command output into a list
    local_directories = list_cloud.stdout.split("\n")[0:-1]

    print(f"In the local copy we have: \n{local_directories}")

    # create a list with the differences between the two lists above
    new_files = list(set(cloud_directories) - set(local_directories))

    return new_files


def sync_directories(remote_folder, local_folder):
    """
    A function that syncs a remote folder with a local folder
    with rclone. 
    """
    sync = subprocess.run(
        ["rclone", "sync", f"remote:{remote_folder}", local_folder]
    )

    print("Syncing local directory with cloud....")
    return sync.returncode


def run_notebook(excel_report, template_notebook):
    """
    A function that runs a notebook against an excel report
    via papermill. 
    """
    no_extension_name = excel_report.split(".")[0]
    papermill.execute_notebook(
        template_notebook,
        f"{no_extension_name}.ipynb",
        parameters=dict(filename=excel_report),
    )
    return no_extension_name


def generate_html_report(notebook_file):
    """
    A function that converts a notebook into an html
    file. 
    """
    generate = subprocess.run(
        ["jupyter", "nbconvert", notebook_file, "--to=html"]
    )
    print("HTML Report was generated")
    return True


def push_to_cloud(remote_folder, filename):
    """
    A function that pushes to a remote cloud folder
    a specific file. 
    """

    push = subprocess.run(
        ["rclone", "copy", filename, f"remote:{remote_folder}"]
    )
    print("Report Published!!!")

def main():
    print("Starting updater..")

    # detect if there are new files in the remote folder
    new_files = get_new_files(
        remote_folder=REMOTE_FOLDER, local_folder=LOCAL_FOLDER
    )

    # if there are none, exit
    if not new_files:
        print("Everything is synced. No new files.")
        sys.exit()
    # else, continue
    else:
        print("There are files missing.")
        print(new_files)

    # sync directories to get new excel report
    sync_directories(remote_folder=REMOTE_FOLDER, local_folder=LOCAL_FOLDER)

    # generate new notebook and extract the name
    clean_name = run_notebook(new_files[0])

    # the new notebook generate will have the following name
    notebook_name = f"{clean_name}.ipynb"

    # generate the html report from the notebook
    generate_html_report(notebook_name)

    # the notebook name will be the following
    html_report_name = f"{clean_name}.html"

    # push the new notebook to the cloud
    push_to_cloud(html_report=html_report_name, remote_folder=ONEDRIVE_FOLDER)

    # make sure everything is synced again
    sync_directories(remote_folder=REMOTE_FOLDER, local_folder=LOCAL_FOLDER)

    print("Updater finished.")

    return True


if __name__ == "main":
    main()
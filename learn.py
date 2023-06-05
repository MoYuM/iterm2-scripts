#!/usr/bin/env python3

import iterm2
import json
import asyncio

DYNAMIC_PROFILE_PATH = "/Users/moyum/Library/Application Support/iTerm2/DynamicProfiles/profiles.json"
WORKING_DIRECTORY_PATH = "/Users/moyum/Desktop"

import os

def get_git_repositories(directory):
    git_repositories = []

    for root, dirs, _ in os.walk(directory):
        if ".git" in dirs:
            git_repositories.append(os.path.basename(root))

    return "\n".join(git_repositories) 

async def run_subprocess(command, cwd):
    process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, cwd=cwd)
    output, _ = await process.communicate()
    return output.decode().strip()

async def create_working_tree(project_name, folder_name, branch_name):
    cwd = WORKING_DIRECTORY_PATH + '/' + project_name
    await run_subprocess(['git','pull'], cwd)
    await run_subprocess(['git','worktree','add',WORKING_DIRECTORY_PATH + "/" + folder_name,branch_name], cwd)

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    if window is not None:
        all_git_repositories = get_git_repositories(WORKING_DIRECTORY_PATH)

        # 获取用户输入的 profile 名称
        alert = iterm2.TextInputAlert("Input", "New Profile Name", "Please input", "")
        folder = iterm2.TextInputAlert("Input", "New working tree folder path, it will add in ../" , "Please input", "")
        project = iterm2.TextInputAlert("Input", "What is your working project name?"+ "\n Here are the available repositories:\n" + all_git_repositories, "Please input", "")
        branch = iterm2.TextInputAlert("Input", "What is your working branch name?", "Please input", "")

        profile_name = await alert.async_run(connection)
        folder_name = await folder.async_run(connection)
        project_name = await project.async_run(connection)
        branch_name = await branch.async_run(connection)

        await create_working_tree(project_name,folder_name, branch_name)

        with open(DYNAMIC_PROFILE_PATH, "r") as file:
            data = json.load(file)
            data['Profiles'].append({
                "Name": profile_name,
                "Guid": profile_name,
                "Badge Text": profile_name,
                "Working Directory": WORKING_DIRECTORY_PATH + "/" + folder_name, 
                "Custom Directory" : "Yes",
                "Bound Hosts" : [
                    WORKING_DIRECTORY_PATH + "/" + folder_name
                ],
            })
        # 保存修改后的数据
        with open(DYNAMIC_PROFILE_PATH, "w") as file:
            json.dump(data, file)

        await window.async_create_tab(command=[f"cd {WORKING_DIRECTORY_PATH}/{folder_name}"])
    else:
        print("No current window")
    

iterm2.run_until_complete(main)

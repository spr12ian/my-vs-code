# my-vs-code
VisualStudio repository

Windows
Install and configure WSL because I plan to only do development in a Linux environment
Download and run VS Code from the Microsoft store

In VS Code install the Microsoft WSL extension
=====================================================
WSL Linux
As per Windows, the installed WSL extension should mean you can use the code command in WSL Linux to run VS code 'remotely'.


=====================================================

https://code.visualstudio.com/docs/editor/settings-sync

Use the built-in **Settings Sync** feature in VS Code to synchronize your settings, keybindings, installed extensions, and other configurations across multiple machines:

### **Step-by-Step Guide to Enable Settings Sync**

1. **Open VS Code**:
   - Launch Visual Studio Code on your machine.

2. **Sign In**:
   - Click on the **Accounts** icon in the Activity Bar (it looks like a person).
   - Select **Turn on Settings Sync**.
   - Choose your preferred authentication method (Microsoft or GitHub account) and sign in.

3. **Configure Sync**:
   - After signing in, you’ll be prompted to configure what you want to sync.
   - You can choose to sync **Settings**, **Keybindings**, **Extensions**, **User Snippets**, and **UI State**.
   - Select the items you want to sync and click **Turn On**.

4. **Automatic Sync**:
   - VS Code will now automatically sync your selected configurations to the cloud.
   - Any changes you make to your settings, keybindings, extensions, snippets, or UI state will be uploaded and synced to your account.

### **Syncing Across Multiple Machines**

1. **Repeat Steps on Other Machines**:
   - On your other machines, repeat the steps above to sign in and turn on Settings Sync.
   - Once signed in, VS Code will automatically download and apply your synced settings and configurations.

2. **Managing Conflicts**:
   - If there are conflicts between your local settings and the cloud settings, you’ll be prompted to **Merge** or **Replace**. Choose the appropriate option based on your needs.

### **Additional Tips**

- **Manual Sync**: If you need to manually sync your settings, you can use the command palette (`Ctrl+Shift+P`) and type `Settings Sync: Sync Now`.
- **Selective Sync**: You can update which items to sync by going to the settings (`Ctrl+,`) and searching for `Settings Sync`, then adjusting your preferences.
- **Account Switching**: If you need to switch accounts or manage your sync settings, you can do so from the **Accounts** icon in the Activity Bar.

By using the built-in Settings Sync feature, you can ensure that your VS Code environment is consistent and up-to-date across all your devices. Let me know if you need any further assistance or have other questions!



=======================================================
VS Code
Add extensions:
For bash development
Bash IDE - Mars Hartmann
ShellCheck - Timon Wong
shfmt - Martin Kühl
For Python development
Black Formatter - Microsoft
Pylance - Microsoft
Python - Microsoft
Python Debugger - Microsoft

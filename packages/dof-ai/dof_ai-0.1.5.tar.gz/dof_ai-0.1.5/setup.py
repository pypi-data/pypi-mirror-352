"""Setup script with custom install command to show ASCII art."""

from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        # Print ASCII art after installation
        print("""
██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║█████╗  
██║  ██║██║   ██║██╔══╝  
██████╔╝╚██████╔╝██║     
╚═════╝  ╚═════╝ ╚═╝     
LangChain for Robotics 🤖

🎉 dof-ai has been successfully installed! 🎉
""")


if __name__ == "__main__":
    setup(
        cmdclass={
            "install": PostInstallCommand,
        },
    )

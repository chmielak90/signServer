current_pwd := $(shell cd)

all: clean build

build:
	@echo "Building..."
	cmd /C "$(current_pwd)\venv\Scripts\activate.bat && python --version && pip install -r requirements.txt"
	cmd /C "$(current_pwd)\venv\Scripts\activate.bat && create-version-file Client\metadata.yml --outfile Client\file_version_info.txt"
	cmd /C "$(current_pwd)\venv\Scripts\activate.bat && pyinstaller --onefile --distpath dist\Client --version-file=Client\file_version_info.txt Client\client.py"
	cmd /C "copy Client\config.ini dist\Client"
	cmd /C "$(current_pwd)\venv\Scripts\activate.bat && create-version-file Server\metadata.yml --outfile Server\file_version_info.txt"
	cmd /C "$(current_pwd)\venv\Scripts\activate.bat && pyinstaller --onefile --distpath dist\Server --version-file=Server\file_version_info.txt Server\server.py"
	cmd /C "copy Server\config.ini dist\Server"
	cmd /C "mkdir dist\Server\allowed_clients"
	cmd /C "echo Here paste client cert in pem format > dist\Server\allowed_clients\readme.txt"
	cmd /C "move dist SignServer"
	cmd /C "powershell Compress-Archive -Path SignServer -DestinationPath SignServer.zip"
	@echo  "Done!"

clean:
	@echo "Cleaning..."
	cmd /C "if exist dist rmdir /S /Q dist"
	cmd /C "if exist signServer rmdir /S /Q signServer"
	cmd /C "if exist build rmdir /S /Q build"
	cmd /C "if exist Client\file_version_info.txt del /F Client\file_version_info.txt"
	cmd /C "if exist Server\file_version_info.txt del /F Server\file_version_info.txt"
	cmd /C "if exist client.spec del /F client.spec"
	cmd /C "if exist server.spec del /F server.spec"
	cmd /C "if exist signServer.zip del /F signServer.zip"
	@echo  "Cleaning done!"

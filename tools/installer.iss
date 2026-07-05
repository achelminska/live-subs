; LiveSubs Windows installer — build with: .\tools\release.ps1
; Requires Inno Setup 6: https://jrsoftware.org/isdl.php

#define MyAppName "LiveSubs"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "LiveSubs"
#define MyAppExeName "LiveSubs.exe"

[Setup]
AppId={{A3B8F2E1-9C4D-4A7B-8E2F-1D5C6B9A0E3F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=LiveSubs-Setup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\LICENSE
InfoBeforeFile=..\tools\installer-welcome.txt

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
var
  ApiKeyPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  ApiKeyPage := CreateInputQueryPage(wpSelectDir,
    'Klucz API DeepL',
    'Tlumaczenie EN -> PL wymaga darmowego klucza DeepL.',
    'Wejdz na deepl.com/pro-api, zaloz konto (plan Free) i wklej klucz ponizej.' + #13#10 + #13#10 +
    'Mozesz tez zostawic pole puste i uzupelnic plik .env recznie pozniej.');
  ApiKeyPage.Add('DEEPL_API_KEY:', False);
end;

function IsValidApiKey(const Key: String): Boolean;
begin
  Result := (Length(Key) >= 20) and (Pos(':', Key) > 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Key: String;
  EnvContent: String;
  EnvPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    Key := Trim(ApiKeyPage.Values[0]);
    EnvPath := ExpandConstant('{app}\.env');

    if Key <> '' then
      EnvContent := 'DEEPL_API_KEY=' + Key + #13#10
    else
      EnvContent := '# Uzupelnij klucz DeepL (darmowy plan: deepl.com/pro-api)' + #13#10 +
                    'DEEPL_API_KEY=' + #13#10;

    SaveStringToFile(EnvPath, EnvContent, False);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Key: String;
begin
  Result := True;
  if CurPageID = ApiKeyPage.ID then
  begin
    Key := Trim(ApiKeyPage.Values[0]);
    if (Key <> '') and (not IsValidApiKey(Key)) then
    begin
      if MsgBox('Klucz wyglada nieprawidlowo (powinien zawierac dwukropek, np. xxxx:fx).' + #13#10 +
                'Kontynuowac mimo to?', mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\livesubs.log"

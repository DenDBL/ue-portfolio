// Copyright Epic Games, Inc. All Rights Reserved.

#include "MFA_AnimAI.h"
#include "MFA_AnimAIStyle.h"
#include "MFA_AnimAICommands.h"
#include "Misc/MessageDialog.h"
#include "ToolMenus.h"
#include "Interfaces/IPluginManager.h"
#include "IPythonScriptPlugin.h"

static const FName MFA_AnimAITabName("MFA_AnimAI");

#define LOCTEXT_NAMESPACE "FMFA_AnimAIModule"

void FMFA_AnimAIModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	
	FMFA_AnimAIStyle::Initialize();
	FMFA_AnimAIStyle::ReloadTextures();

	FMFA_AnimAICommands::Register();
	
	PluginCommands = MakeShareable(new FUICommandList);

	PluginCommands->MapAction(
		FMFA_AnimAICommands::Get().PluginAction,
		FExecuteAction::CreateRaw(this, &FMFA_AnimAIModule::PluginButtonClicked),
		FCanExecuteAction());

	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMFA_AnimAIModule::RegisterMenus));
}

void FMFA_AnimAIModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.

	UToolMenus::UnRegisterStartupCallback(this);

	UToolMenus::UnregisterOwner(this);

	FMFA_AnimAIStyle::Shutdown();

	FMFA_AnimAICommands::Unregister();
}

void FMFA_AnimAIModule::PluginButtonClicked()
{
	FPythonCommandEx Cmd;

	auto PluginPath = IPluginManager::Get().FindPlugin("MFA_AnimAI")->GetBaseDir();
	Cmd.Command = PluginPath / "Content/Python/Source/main.py";
	Cmd.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
	IPythonScriptPlugin::Get()->ExecPythonCommandEx(Cmd);
}

void FMFA_AnimAIModule::RegisterMenus()
{
	// Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
	FToolMenuOwnerScoped OwnerScoped(this);

	{
		UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
		{
			FToolMenuSection& Section = Menu->FindOrAddSection("WindowLayout");
			Section.AddMenuEntryWithCommandList(FMFA_AnimAICommands::Get().PluginAction, PluginCommands);
		}
	}

	{
		UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar.PlayToolBar");
		{
			FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("PluginTools");
			{
				FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitToolBarButton(FMFA_AnimAICommands::Get().PluginAction));
				Entry.SetCommandList(PluginCommands);
			}
		}
	}
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FMFA_AnimAIModule, MFA_AnimAI)
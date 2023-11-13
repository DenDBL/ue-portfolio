// Copyright Epic Games, Inc. All Rights Reserved.

#include "Facial_ControlRig_Builder.h"
#include "Facial_ControlRig_BuilderStyle.h"
#include "Facial_ControlRig_BuilderCommands.h"
#include "Misc/MessageDialog.h"
#include "ToolMenus.h"
#include "Interfaces/IPluginManager.h"
#include "IPythonScriptPlugin.h"

static const FName Facial_ControlRig_BuilderTabName("Facial_ControlRig_Builder");

#define LOCTEXT_NAMESPACE "FFacial_ControlRig_BuilderModule"

void FFacial_ControlRig_BuilderModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	
	FFacial_ControlRig_BuilderStyle::Initialize();
	FFacial_ControlRig_BuilderStyle::ReloadTextures();

	FFacial_ControlRig_BuilderCommands::Register();
	
	PluginCommands = MakeShareable(new FUICommandList);

	PluginCommands->MapAction(
		FFacial_ControlRig_BuilderCommands::Get().PluginAction,
		FExecuteAction::CreateRaw(this, &FFacial_ControlRig_BuilderModule::PluginButtonClicked),
		FCanExecuteAction());

	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FFacial_ControlRig_BuilderModule::RegisterMenus));
}

void FFacial_ControlRig_BuilderModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.

	UToolMenus::UnRegisterStartupCallback(this);

	UToolMenus::UnregisterOwner(this);

	FFacial_ControlRig_BuilderStyle::Shutdown();

	FFacial_ControlRig_BuilderCommands::Unregister();
}

void FFacial_ControlRig_BuilderModule::PluginButtonClicked()
{
	// Put your "OnButtonClicked" stuff here
	/*
	
	*/
	FPythonCommandEx Cmd;

	auto PluginPath = IPluginManager::Get().FindPlugin("Facial_ControlRig_Builder")->GetBaseDir();
	Cmd.Command = PluginPath / "Content/Python/face_rig_generator.py";
	Cmd.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
	IPythonScriptPlugin::Get()->ExecPythonCommandEx(Cmd);
}

void FFacial_ControlRig_BuilderModule::RegisterMenus()
{
	// Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
	FToolMenuOwnerScoped OwnerScoped(this);

	{
		UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
		{
			FToolMenuSection& Section = Menu->FindOrAddSection("WindowLayout");
			Section.AddMenuEntryWithCommandList(FFacial_ControlRig_BuilderCommands::Get().PluginAction, PluginCommands);
		}
	}

	{
		UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar.PlayToolBar");
		{
			FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("PluginTools");
			{
				FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitToolBarButton(FFacial_ControlRig_BuilderCommands::Get().PluginAction));
				Entry.SetCommandList(PluginCommands);
			}
		}
	}
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FFacial_ControlRig_BuilderModule, Facial_ControlRig_Builder)
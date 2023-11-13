// Copyright Epic Games, Inc. All Rights Reserved.

#include "Facial_ControlRig_BuilderCommands.h"

#define LOCTEXT_NAMESPACE "FFacial_ControlRig_BuilderModule"

void FFacial_ControlRig_BuilderCommands::RegisterCommands()
{
	UI_COMMAND(PluginAction, "Facial_ControlRig_Builder", "Execute Facial_ControlRig_Builder action", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE

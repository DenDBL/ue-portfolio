// Copyright Epic Games, Inc. All Rights Reserved.

#include "MFA_AnimAICommands.h"

#define LOCTEXT_NAMESPACE "FMFA_AnimAIModule"

void FMFA_AnimAICommands::RegisterCommands()
{
	UI_COMMAND(PluginAction, "MFA_AnimAI", "Execute MFA_AnimAI action", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE

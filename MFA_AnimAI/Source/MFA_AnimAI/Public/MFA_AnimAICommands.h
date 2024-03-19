// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Framework/Commands/Commands.h"
#include "MFA_AnimAIStyle.h"

class FMFA_AnimAICommands : public TCommands<FMFA_AnimAICommands>
{
public:

	FMFA_AnimAICommands()
		: TCommands<FMFA_AnimAICommands>(TEXT("MFA_AnimAI"), NSLOCTEXT("Contexts", "MFA_AnimAI", "MFA_AnimAI Plugin"), NAME_None, FMFA_AnimAIStyle::GetStyleSetName())
	{
	}

	// TCommands<> interface
	virtual void RegisterCommands() override;

public:
	TSharedPtr< FUICommandInfo > PluginAction;
};

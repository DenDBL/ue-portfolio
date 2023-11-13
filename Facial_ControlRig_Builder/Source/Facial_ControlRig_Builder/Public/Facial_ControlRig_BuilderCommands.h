// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Framework/Commands/Commands.h"
#include "Facial_ControlRig_BuilderStyle.h"

class FFacial_ControlRig_BuilderCommands : public TCommands<FFacial_ControlRig_BuilderCommands>
{
public:

	FFacial_ControlRig_BuilderCommands()
		: TCommands<FFacial_ControlRig_BuilderCommands>(TEXT("Facial_ControlRig_Builder"), NSLOCTEXT("Contexts", "Facial_ControlRig_Builder", "Facial_ControlRig_Builder Plugin"), NAME_None, FFacial_ControlRig_BuilderStyle::GetStyleSetName())
	{
	}

	// TCommands<> interface
	virtual void RegisterCommands() override;

public:
	TSharedPtr< FUICommandInfo > PluginAction;
};

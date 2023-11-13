// Copyright Epic Games, Inc. All Rights Reserved.

#include "Facial_ControlRig_BuilderStyle.h"
#include "Facial_ControlRig_Builder.h"
#include "Framework/Application/SlateApplication.h"
#include "Styling/SlateStyleRegistry.h"
#include "Slate/SlateGameResources.h"
#include "Interfaces/IPluginManager.h"
#include "Styling/SlateStyleMacros.h"

#define RootToContentDir Style->RootToContentDir

TSharedPtr<FSlateStyleSet> FFacial_ControlRig_BuilderStyle::StyleInstance = nullptr;

void FFacial_ControlRig_BuilderStyle::Initialize()
{
	if (!StyleInstance.IsValid())
	{
		StyleInstance = Create();
		FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);
	}
}

void FFacial_ControlRig_BuilderStyle::Shutdown()
{
	FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
	ensure(StyleInstance.IsUnique());
	StyleInstance.Reset();
}

FName FFacial_ControlRig_BuilderStyle::GetStyleSetName()
{
	static FName StyleSetName(TEXT("Facial_ControlRig_BuilderStyle"));
	return StyleSetName;
}


const FVector2D Icon16x16(16.0f, 16.0f);
const FVector2D Icon20x20(20.0f, 20.0f);

TSharedRef< FSlateStyleSet > FFacial_ControlRig_BuilderStyle::Create()
{
	TSharedRef< FSlateStyleSet > Style = MakeShareable(new FSlateStyleSet("Facial_ControlRig_BuilderStyle"));
	Style->SetContentRoot(IPluginManager::Get().FindPlugin("Facial_ControlRig_Builder")->GetBaseDir() / TEXT("Resources"));

	Style->Set("Facial_ControlRig_Builder.PluginAction", new IMAGE_BRUSH(TEXT("FaceRigButton"), Icon20x20));
	return Style;
}

void FFacial_ControlRig_BuilderStyle::ReloadTextures()
{
	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().GetRenderer()->ReloadTextureResources();
	}
}

const ISlateStyle& FFacial_ControlRig_BuilderStyle::Get()
{
	return *StyleInstance;
}

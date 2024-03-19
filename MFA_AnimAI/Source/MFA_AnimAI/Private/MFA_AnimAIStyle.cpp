// Copyright Epic Games, Inc. All Rights Reserved.

#include "MFA_AnimAIStyle.h"
#include "MFA_AnimAI.h"
#include "Framework/Application/SlateApplication.h"
#include "Styling/SlateStyleRegistry.h"
#include "Slate/SlateGameResources.h"
#include "Interfaces/IPluginManager.h"
#include "Styling/SlateStyleMacros.h"

#define RootToContentDir Style->RootToContentDir

TSharedPtr<FSlateStyleSet> FMFA_AnimAIStyle::StyleInstance = nullptr;

void FMFA_AnimAIStyle::Initialize()
{
	if (!StyleInstance.IsValid())
	{
		StyleInstance = Create();
		FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);
	}
}

void FMFA_AnimAIStyle::Shutdown()
{
	FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
	ensure(StyleInstance.IsUnique());
	StyleInstance.Reset();
}

FName FMFA_AnimAIStyle::GetStyleSetName()
{
	static FName StyleSetName(TEXT("MFA_AnimAIStyle"));
	return StyleSetName;
}


const FVector2D Icon16x16(16.0f, 16.0f);
const FVector2D Icon20x20(20.0f, 20.0f);

TSharedRef< FSlateStyleSet > FMFA_AnimAIStyle::Create()
{
	TSharedRef< FSlateStyleSet > Style = MakeShareable(new FSlateStyleSet("MFA_AnimAIStyle"));
	Style->SetContentRoot(IPluginManager::Get().FindPlugin("MFA_AnimAI")->GetBaseDir() / TEXT("Resources"));

	Style->Set("MFA_AnimAI.PluginAction", new IMAGE_BRUSH(TEXT("AnimAI"), Icon20x20));
	return Style;
}

void FMFA_AnimAIStyle::ReloadTextures()
{
	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().GetRenderer()->ReloadTextureResources();
	}
}

const ISlateStyle& FMFA_AnimAIStyle::Get()
{
	return *StyleInstance;
}

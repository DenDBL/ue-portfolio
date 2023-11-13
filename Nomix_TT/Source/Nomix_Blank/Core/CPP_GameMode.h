// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CPP_GameMode.generated.h"

/**
 * 
 */
UCLASS()
class NOMIX_BLANK_API ACPP_GameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Character")
		float interactionRadius = 100;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Character")
		int numberOfSlots = 2;
	
};

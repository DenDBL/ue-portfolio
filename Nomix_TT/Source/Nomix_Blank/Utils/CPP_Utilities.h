// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CPP_Utilities.generated.h"

/**
 * 
 */
UENUM(BlueprintType)
enum class ECardTypes : uint8 {
    ECT_None      UMETA(DisplayName = "None"),
    ECT_Red       UMETA(DisplayName = "Red"),
    ECT_Blue        UMETA(DisplayName = "Blue"),
};

UCLASS()
class NOMIX_BLANK_API UCPP_Utilities : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
	
};

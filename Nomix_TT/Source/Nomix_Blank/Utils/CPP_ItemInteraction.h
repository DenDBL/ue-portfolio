// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "CPP_ItemInteraction.generated.h"

// This class does not need to be modified.
UINTERFACE(MinimalAPI)
class UCPP_ItemInteraction : public UInterface
{
	GENERATED_BODY()
};

/**
 * 
 */
class NOMIX_BLANK_API ICPP_ItemInteraction
{
	GENERATED_BODY()

	// Add interface functions to this class. This is the class that will be inherited to implement this interface.
public:

	UFUNCTION()
		virtual void PickUpItem(AActor* Actor) { return; };

	UFUNCTION()
		virtual void TriggerItemStart(AActor* Actor) { return; };

	UFUNCTION()
		virtual void TriggerItemStop(AActor* Actor) { return; };

	UFUNCTION()
		virtual void HandleMouseXDrag(AActor* Actor) { return; };
};

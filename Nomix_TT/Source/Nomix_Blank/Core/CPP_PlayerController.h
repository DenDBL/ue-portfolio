// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "CPP_Char.h"
#include "CPP_PlayerController.generated.h"


/**
 * 
 */
UCLASS()
class NOMIX_BLANK_API ACPP_PlayerController : public APlayerController
{
	GENERATED_BODY()

	

public:
	ACPP_PlayerController();
	
	UPROPERTY()
		float axisValueLookRight = 0;

protected:
	virtual void BeginPlay() override;
private:
	bool bIsTriggering = false;
	
	virtual void SetupInputComponent() override;

	ACPP_Char* ControlledCharacter;
	UFUNCTION()
		void OnMoveForward(float Value);
	UFUNCTION()
		void OnMoveRight(float Value);
	UFUNCTION()
		void OnLookUp(float Value);
	UFUNCTION()
		void OnLookRight(float Value);
	UFUNCTION()
		void PickUpItem();
	UFUNCTION()
		void TriggerItemStart();
	UFUNCTION()
		void TriggerItemStop();
	UFUNCTION()
		void ChooseFirstSlot();
	UFUNCTION()
		void ChooseSecondSlot();
};

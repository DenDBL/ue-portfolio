// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerController.h"
#include "CPP_PlayerController.h"
#include "../Utils/CPP_ItemInteraction.h"
#include "CPP_Char.h"

#include "CPP_Valve.generated.h"


UCLASS()
class NOMIX_BLANK_API ACPP_Valve : public AActor, public ICPP_ItemInteraction
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ACPP_Valve();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	virtual void TriggerItemStart(AActor* Actor) override;

	virtual void TriggerItemStop(AActor* Actor) override;

	virtual void HandleMouseXDrag(AActor* Actor) override;
};

// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CPP_Char.h"
#include "../Utils/CPP_ItemInteraction.h"
#include "../Utils/CPP_Utilities.h"
#include "CPP_Card.generated.h"

UCLASS()
class NOMIX_BLANK_API ACPP_Card : public AActor, public ICPP_ItemInteraction
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ACPP_Card();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;
	virtual void PickUpItem(AActor* Actor) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Access")
		ECardTypes cardType = ECardTypes::ECT_None;

};

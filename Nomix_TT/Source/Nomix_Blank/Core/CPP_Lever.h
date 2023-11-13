// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CPP_Char.h"
#include "../Utils/CPP_ItemInteraction.h"
#include "CPP_Lever.generated.h"

UDELEGATE(BlueprintAuthorityOnly)
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPullStartDelegate);
UDELEGATE(BlueprintAuthorityOnly)
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPullStopDelegate);

UCLASS()
class NOMIX_BLANK_API ACPP_Lever : public AActor, public ICPP_ItemInteraction
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ACPP_Lever();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Using")
		float maxAngle = 45;

	UPROPERTY(BlueprintAssignable, Category = "Using")
		FOnPullStartDelegate OnPullStart;
	UPROPERTY(BlueprintAssignable, Category = "Using")
		FOnPullStopDelegate OnPullStop;

	UFUNCTION()
		virtual void TriggerItemStart(AActor* Actor) override;
	UFUNCTION()
		virtual void TriggerItemStop(AActor* Actor) override;
};

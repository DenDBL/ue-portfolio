// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "../Utils/CPP_ItemInteraction.h"
#include "../Utils/CPP_Utilities.h"
#include "CPP_Char.h"
#include "CPP_Card.h"
#include "CPP_Validator.generated.h"


UDELEGATE(BlueprintAuthorityOnly)
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnAccessGrantedDelegate);
UDELEGATE(BlueprintAuthorityOnly)
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnAccessDeniedDelegate);

UCLASS()
class NOMIX_BLANK_API ACPP_Validator : public AActor, public ICPP_ItemInteraction
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ACPP_Validator();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;
	UPROPERTY(BlueprintAssignable, Category = "Access")
		FOnAccessGrantedDelegate OnAccessGranted;
	UPROPERTY(BlueprintAssignable, Category = "Access")
		FOnAccessDeniedDelegate OnAccessDenied;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Access")
		TArray<ECardTypes> allowedCardTypes;
	UFUNCTION()
		virtual void TriggerItemStart(AActor* Actor) override;
};

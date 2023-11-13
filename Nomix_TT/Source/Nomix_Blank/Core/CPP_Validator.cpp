// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Validator.h"

// Sets default values
ACPP_Validator::ACPP_Validator()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void ACPP_Validator::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ACPP_Validator::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

void ACPP_Validator::TriggerItemStart(AActor* Actor)
{
	ACPP_Char* character = Cast<ACPP_Char>(Actor);
	if (!character)
		return;

	ACPP_Card* card = Cast<ACPP_Card>(character->InventoryComponent->GetSelectedItem());
	if (card)
		if (allowedCardTypes.Contains(card->cardType))
			OnAccessGranted.Broadcast();
		else
			OnAccessDenied.Broadcast();

}


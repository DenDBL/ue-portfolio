// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Valve.h"

// Sets default values
ACPP_Valve::ACPP_Valve()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void ACPP_Valve::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ACPP_Valve::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

void ACPP_Valve::TriggerItemStart(AActor* Actor) {
	ACPP_Char* character = Cast<ACPP_Char>(Actor);

	if (!character)
		return;
	
	character->SetFreezed(true);
}

void ACPP_Valve::TriggerItemStop(AActor* Actor) {

	ACPP_Char* character = Cast<ACPP_Char>(Actor);

	if (!character)
		return;

	character->SetFreezed(false);
}

void ACPP_Valve::HandleMouseXDrag(AActor* Actor) {

	
	ACPP_PlayerController* PlayerController = Cast<ACPP_PlayerController>(GetWorld()->GetFirstPlayerController());

	if (PlayerController)
	{
		RootComponent->AddLocalRotation(FRotator(0.f, PlayerController->axisValueLookRight, 0.f));
		//AddActorWorldRotation(FRotator(0.f, PlayerController->axisValueLookRight, 0.f));
	}
}
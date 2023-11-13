// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Lever.h"

// Sets default values
ACPP_Lever::ACPP_Lever()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void ACPP_Lever::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ACPP_Lever::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

void ACPP_Lever::TriggerItemStart(AActor* Actor) {
	ACPP_Char* character = Cast<ACPP_Char>(Actor);

	if (!character)
		return;

	OnPullStart.Broadcast();
}

void ACPP_Lever::TriggerItemStop(AActor* Actor) {

	ACPP_Char* character = Cast<ACPP_Char>(Actor);

	if (!character)
		return;

	OnPullStop.Broadcast();
}

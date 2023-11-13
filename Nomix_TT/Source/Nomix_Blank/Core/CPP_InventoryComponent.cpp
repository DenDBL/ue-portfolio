// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_InventoryComponent.h"
#include "CPP_GameMode.h"
// Sets default values for this component's properties
UCPP_InventoryComponent::UCPP_InventoryComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	InitSlots();
}


// Called when the game starts
void UCPP_InventoryComponent::BeginPlay()
{
	Super::BeginPlay();

	ACPP_GameMode* CurrentGameMode = Cast<ACPP_GameMode>(GetWorld()->GetAuthGameMode());

	if (CurrentGameMode)
		slotsCount = CurrentGameMode->numberOfSlots;
	
	InitSlots();
	
}


// Called every frame
void UCPP_InventoryComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

void UCPP_InventoryComponent::InitSlots()
{
	if (slotsCount == 0)
		return;

	slots.Empty();

	for (int i = 0; i < slotsCount; i++) {
		slots.Add(nullptr);
	}
}

void UCPP_InventoryComponent::AddItemToInventory(AActor* item)
{
	if (slots.Num() == 0)
		return;

	for (int i = 0; i < slotsCount ;i++) {
		if (!slots[i]) {
			slots[i] = item;
			UpdateSelectedSlot();
			break;
		}
	}
	
}

void UCPP_InventoryComponent::UpdateSelectedSlot()
{
	for (auto& slot : slots) {
		if (slot) {
			slot->SetActorHiddenInGame(true);
			//slot->SetActorEnableCollision(false);
		}
	}

	AActor* selectedActor = slots[selectedSlot];
	if (selectedActor) {
		selectedActor->SetActorHiddenInGame(false);
	}

}

void UCPP_InventoryComponent::SelectSlot(int number)
{	
	number = FMath::Clamp(number, 0, slotsCount - 1);

	selectedSlot = number;
	UpdateSelectedSlot();
}

AActor* UCPP_InventoryComponent::GetSelectedItem()
{
	return slots[selectedSlot];
}


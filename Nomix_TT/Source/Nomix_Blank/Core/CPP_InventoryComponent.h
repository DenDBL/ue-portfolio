// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CPP_InventoryComponent.generated.h"


UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class NOMIX_BLANK_API UCPP_InventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UCPP_InventoryComponent();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UPROPERTY()
		int	slotsCount = 0;
	UPROPERTY()
		int	selectedSlot = 0;
	UPROPERTY()
		TArray<AActor*> slots;

	UFUNCTION()
		void InitSlots();
	UFUNCTION()
		void AddItemToInventory(AActor* item);
	UFUNCTION()
		void UpdateSelectedSlot();
	UFUNCTION()
		void SelectSlot(int number);
	UFUNCTION()
		AActor* GetSelectedItem();
};

// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CPP_GameMode.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "../Utils/CPP_ItemInteraction.h"
#include "CPP_InventoryComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SphereComponent.h"
#include "Components/ArrowComponent.h"
#include "Camera/CameraComponent.h" 
#include "CPP_Char.generated.h"



UCLASS()
class NOMIX_BLANK_API ACPP_Char : public ACharacter
{
	GENERATED_BODY()

public:
	// Sets default values for this character's properties
	ACPP_Char();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
		UCameraComponent* CameraComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
		USkeletalMeshComponent* SkeletalMeshComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
		UCharacterMovementComponent* MovementComponent;

	UPROPERTY()
		bool freezed = false;
	

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	// Called to bind functionality to input
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Inventory")
		UCPP_InventoryComponent* InventoryComponent;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
		UArrowComponent* RightHand;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Collision")
		USphereComponent* SphereCollisionComponent;
	UPROPERTY()
		AActor* objectInAction = nullptr;

	UFUNCTION()
		void MoveForward(float value);
	UFUNCTION()
		void MoveRight(float value);
	UFUNCTION()
		void LookUp(float value);
	UFUNCTION()
		void LookRight(float value);
	UFUNCTION()
		void PickUpItem();
	UFUNCTION()
		void UseItemStart(AActor* item = nullptr);
	UFUNCTION(BlueprintCallable)
		void UseItemStop(AActor* item = nullptr);
	UFUNCTION(BlueprintCallable)
		AActor* LookingAtActor();
	UFUNCTION()
		void ChooseSlot(int number);
	UFUNCTION()
		void SetFreezed(bool bFreez) { freezed = bFreez; }
};	

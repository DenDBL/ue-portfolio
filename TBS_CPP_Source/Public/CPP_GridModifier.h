// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "CPP_Utility.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Actor.h"
#include "CPP_GridModifier.generated.h"

UCLASS()
class TBS_PROJECT_API ACPP_GridModifier : public AActor
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Components")
		class USceneComponent* SceneRoot = nullptr;
	
	


public:	
	// Sets default values for this actor's properties
	ACPP_GridModifier();


protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	virtual void OnConstruction(const FTransform& Transform) override;

	FColor GetColorBasedOnType(TileType type);

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Data")
		class UDataTable* gridShapeDataTable = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Data")
		FName rowName = "Square";

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Type")
		TileType tileType = TileType::Default;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Components")
		class UStaticMeshComponent* staticMesh;

	UFUNCTION(BlueprintImplementableEvent)
		void ModifyTile(FIntPoint index, class ACPP_Grid* grid);

};

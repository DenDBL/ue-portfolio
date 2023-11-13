// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/DataTable.h"
#include "CPP_Utility.h"

#include "CPP_GridVisual.generated.h"


UCLASS()
class TBS_PROJECT_API ACPP_GridVisual : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ACPP_GridVisual();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	UPROPERTY(BlueprintReadWrite, Category = "Grid")
		UDataTable* gridShapeDataTable = nullptr;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	UPROPERTY( BlueprintReadWrite, Category = "Components")
		UInstancedStaticMeshComponent* InstancedStaticMeshComponent = nullptr;

	UPROPERTY( BlueprintReadWrite, Category = "Grid")
		TArray<FIntPoint> instanceIndexes;

	UPROPERTY( BlueprintReadWrite, Category = "Grid")
		class ACPP_Grid* parentGrid;

	UPROPERTY(BlueprintReadWrite, Category = "GridVisual")
		float zOffset = 5;

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void SetGridShapeDataTable(UDataTable* dataTable);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void InitGridVisuals(UDataTable* dataTable, class ACPP_Grid* grid);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void UpdateTileVisual(FTileData data);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void AddInstance(FTileData data);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void RemoveInstance(FIntPoint index);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void ClearInstances();
	
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Grid")
		class ACPP_Grid* GetParentGrid();
	
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GridVisual")
		float GetTileDefaultHeight(FIntPoint index);

	UFUNCTION(BlueprintCallable, Category = "GridVisual")
		void SetInstanceHeight(FIntPoint index, float height);

	UFUNCTION(BlueprintCallable, Category = "GridVisual")
		void SetInstanceMaterialHeight(FIntPoint index, float height);

	UFUNCTION(BlueprintCallable, Category = "GridVisual")
		void SetInstanceColor(FIntPoint index, FLinearColor color);
	
};


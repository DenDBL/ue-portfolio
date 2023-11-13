// Fill out your copyright notice in the Description page of Project Settings.
#include "CPP_GridVisual.h"
#include "CPP_Grid.h"



struct FGridShapeData;

// Sets default values
ACPP_GridVisual::ACPP_GridVisual()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

	
	InstancedStaticMeshComponent = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("InstancedStaticMeshComponent"));
	InstancedStaticMeshComponent->SetCollisionEnabled(ECollisionEnabled::QueryOnly);  // Disable collision
	InstancedStaticMeshComponent->SetCollisionResponseToAllChannels(ECollisionResponse::ECR_Ignore);
	InstancedStaticMeshComponent->SetCollisionResponseToChannel(ECollisionChannel::ECC_GameTraceChannel2,
		ECollisionResponse::ECR_Block);
	InstancedStaticMeshComponent->SetMobility(EComponentMobility::Movable);
	RootComponent = InstancedStaticMeshComponent;

	

}

// Called when the game starts or when spawned
void ACPP_GridVisual::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ACPP_GridVisual::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

void ACPP_GridVisual::SetGridShapeDataTable(UDataTable* dataTable)
{	
	if (dataTable != nullptr && this != nullptr)
	{
		gridShapeDataTable = dataTable;
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("dataTable is nullptr!"));
	}
}

void ACPP_GridVisual::InitGridVisuals(UDataTable* dataTable, ACPP_Grid* grid) 
	{
		
		SetGridShapeDataTable(dataTable);
		parentGrid = grid;

		ClearInstances();

		if (!gridShapeDataTable) {
			UE_LOG(LogTemp, Log, TEXT("Таблица в %s не инициализирована"), *this->GetActorNameOrLabel());
			return;
		}


		FGridShapeData* DataRow;
		
		DataRow = gridShapeDataTable->FindRow<FGridShapeData>(FName("Square"), "Получение строки из таблицы данных GridShapeData");
		InstancedStaticMeshComponent->SetStaticMesh(DataRow->FlatMesh);
		InstancedStaticMeshComponent->SetMaterial(0,DataRow->FlatBorderMaterial);
		//InstancedStaticMeshComponent->SetVectorParameterValueOnMaterials(FName("color"), FVector(255 /255, 255 /255, 255/255));
		InstancedStaticMeshComponent->NumCustomDataFloats = 5;



}

void ACPP_GridVisual::UpdateTileVisual(FTileData data)
{	
	RemoveInstance(data.index);
	if (UCPP_Utility::IsTileWalkable(data)) {
		float offset = zOffset;
		FTileData offsetted = data;
		offsetted.transform.SetLocation(FVector(
			data.transform.GetLocation().X,
			data.transform.GetLocation().Y,
			data.transform.GetLocation().Z + offset)
		);
		AddInstance(offsetted);
		SetInstanceColor(data.index, FColor(255, 255, 255));
	}

}



void ACPP_GridVisual::AddInstance(FTileData data)
{
	RemoveInstance(data.index);
	InstancedStaticMeshComponent->AddInstance(data.transform, true);
	int32 I = instanceIndexes.Add(data.index);



}

void ACPP_GridVisual::RemoveInstance(FIntPoint index)
{
	if (instanceIndexes.Contains(index)) {
		InstancedStaticMeshComponent->RemoveInstance(instanceIndexes.Find(index));
		instanceIndexes.Remove(index);
	}
}

void ACPP_GridVisual::ClearInstances()
{
	InstancedStaticMeshComponent->ClearInstances();
	instanceIndexes.Empty();
}

ACPP_Grid* ACPP_GridVisual::GetParentGrid()
{
	return parentGrid;
}

float ACPP_GridVisual::GetTileDefaultHeight(FIntPoint index)
{	
	float height = parentGrid->GetGridTiles().Find(index)->transform.GetLocation().Z + zOffset;
	return height;
}

void ACPP_GridVisual::SetInstanceHeight(FIntPoint index,float height)
{	
	int32 I = instanceIndexes.Find(index);

	FTransform transform = parentGrid->GetGridTiles().Find(index)->transform;
	
	//InstancedStaticMeshComponent->GetInstanceTransform(I, transform);
	transform.SetLocation(FVector(transform.GetLocation().X, transform.GetLocation().Y, GetTileDefaultHeight(index) + height));

	InstancedStaticMeshComponent->UpdateInstanceTransform(I, transform,true,true,true);

}

void ACPP_GridVisual::SetInstanceMaterialHeight(FIntPoint index, float height)
{
	int32 I = instanceIndexes.Find(index);
	
	bool check = InstancedStaticMeshComponent->SetCustomDataValue(I, 4, height, true);
	//UE_LOG(LogTemp, Log, TEXT("Height:= %s"), check ? TEXT("true") : TEXT("false"));
}

void ACPP_GridVisual::SetInstanceColor(FIntPoint index, FLinearColor color)
{
	int32 I = instanceIndexes.Find(index);

	InstancedStaticMeshComponent->SetCustomDataValue(I, 0, color.R , true);
	InstancedStaticMeshComponent->SetCustomDataValue(I, 1, color.G, true);
	InstancedStaticMeshComponent->SetCustomDataValue(I, 2, color.B, true);
	if(color.A)
		InstancedStaticMeshComponent->SetCustomDataValue(I, 3, color.A, true);


}

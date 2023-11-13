// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_GridModifier.h"

// Sets default values
ACPP_GridModifier::ACPP_GridModifier()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("DefaultSceneRoot"));
	SetRootComponent(SceneRoot);

	staticMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("StaticMeshComponent"));
	staticMesh->SetupAttachment(RootComponent);

	

	

	

}



// Called when the game starts or when spawned
void ACPP_GridModifier::BeginPlay()
{
	Super::BeginPlay();
	
}

void ACPP_GridModifier::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	FGridShapeData* DataRow;

	

	if (gridShapeDataTable)
		DataRow = gridShapeDataTable->FindRow<FGridShapeData>(rowName, "Получение строки из таблицы данных GridShapeData");
	else {
		return;
	}

	staticMesh->SetStaticMesh(DataRow->Mesh);
	staticMesh->SetMaterial(0, DataRow->FlatFilledMaterial);

	FVector normalColor;
	normalColor.X = GetColorBasedOnType(tileType).R / 255.f;
	normalColor.Y = GetColorBasedOnType(tileType).G / 255.f;
	normalColor.Z = GetColorBasedOnType(tileType).B / 255.f;
	staticMesh->SetVectorParameterValueOnMaterials("color", normalColor);

	staticMesh->SetCollisionResponseToAllChannels(ECollisionResponse::ECR_Ignore);
	staticMesh->SetCollisionResponseToChannel(ECollisionChannel::ECC_GameTraceChannel1, ECollisionResponse::ECR_Block);

	SetActorHiddenInGame(true);

}

FColor ACPP_GridModifier::GetColorBasedOnType(TileType type)
{
	switch (type){
		case TileType::None:
			return FColor(0,0,0);
			break;
		case TileType::Default:
			return FColor(255, 255,255);
			break;
		case TileType::Obstacle:
			return FColor(255, 0, 0);
			break;
	}

	return FColor(0,0,0);
}

// Called every frame
void ACPP_GridModifier::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}



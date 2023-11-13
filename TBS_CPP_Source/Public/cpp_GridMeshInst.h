// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "cpp_GridMeshInst.generated.h"

UCLASS()
class TBS_PROJECT_API Acpp_GridMeshInst : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	Acpp_GridMeshInst();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

};

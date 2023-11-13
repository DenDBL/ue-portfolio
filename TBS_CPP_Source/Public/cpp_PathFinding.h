// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Containers/Map.h"
#include "Math/IntPoint.h"
#include "cpp_PathFinding.generated.h"


UCLASS()
class TBS_PROJECT_API Acpp_PathFinding : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	Acpp_PathFinding();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	UFUNCTION(BlueprintCallable, Category = "path")
		TArray<FIntPoint> FindPath(const FIntPoint& Start, const FIntPoint& End, const TMap<FIntPoint, bool>& Map);

	
};

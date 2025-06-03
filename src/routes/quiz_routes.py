from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from typing import List, Tuple

from src.schemas.quiz_schemas import Quiz, Question
from src.database.mongo import quiz_collection


router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("/", response_model=List[Quiz])
async def get_all_quizzes():
    quizzes = await quiz_collection.find().to_list(length=100)  # Adjust length if needed
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found")
    return quizzes
@router.post("/", response_model=Quiz)
async def create_quiz(quiz: Quiz):
    existing_quiz = await quiz_collection.find_one({
        "course_id": quiz.course_id,
        "quiz_number": quiz.quiz_number})
    if existing_quiz:
        raise HTTPException(status_code=400, detail=f"Quiz #{quiz.quiz_number} already exists in this course")

    result = await quiz_collection.insert_one(quiz.dict(by_alias=True))
    created_quiz = await quiz_collection.find_one({"_id": result.inserted_id})

    return created_quiz


@router.get("/course/{course_id}")
async def get_course_quizzes_ids(course_id: int):
    cursor = quiz_collection.find(
        {"course_id": course_id},
        {"quiz_number": 1, "is_active": 1})
    return await cursor.to_list(length=None)


@router.get("/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    quiz = await quiz_collection.find_one({"_id": quiz_id})
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.get("/course/{course_id}/number/{quiz_number}", response_model=Quiz)
async def get_quiz_by_number(course_id: int, quiz_number: int):
    quiz = await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.patch("/course/{course_id}/number/{quiz_number}", response_model=Quiz)
async def add_question(course_id: int, quiz_number: int, question: Question):
    result = await quiz_collection.update_one(
        {"course_id": course_id, "quiz_number": quiz_number},
        {"$push": {"questions": question.dict()}})

    if result.modified_count == 1:
        return await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
    raise HTTPException(status_code=404, detail="Quiz not found")


@router.put("/course/{course_id}/number/{quiz_number}", response_model=Quiz)
async def update_quiz(course_id: int, quiz_number: int, quiz_update: Quiz):
    try:
        # Check if quiz exists
        existing_quiz = await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        if not existing_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Check if update would create duplicate quiz number
        if existing_quiz["quiz_number"] != quiz_update.quiz_number:
            duplicate = await quiz_collection.find_one({
                "course_id": quiz_update.course_id,
                "quiz_number": quiz_update.quiz_number,
            })
            if duplicate:
                raise HTTPException(
                    status_code=400,
                    detail=f"Quiz #{quiz_update.quiz_number} already exists in this course"
                )

        # Update quiz
        update_result = await quiz_collection.update_one(
            {"course_id": course_id, "quiz_number": quiz_number},
            {"$set": quiz_update.dict(by_alias=True, exclude={"id"})}
        )

        if update_result.modified_count == 1:
            return await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/course/{course_id}/quiz/{quiz_number}/question/{question_number}/answers", response_model=Quiz)
async def update_quiz_question_answers(
        course_id: int,
        quiz_number: int,
        question_number: int,
        answers: List[Tuple[bool, str]]
):
    try:
        # Check if quiz exists
        existing_quiz = await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        if not existing_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Check if the question_number is valid
        if question_number < 0 or question_number >= len(existing_quiz["questions"]):
            raise HTTPException(status_code=400, detail="Invalid question number")

        # Update only the answers for the specific question
        update_result = await quiz_collection.update_one(
            {"course_id": course_id, "quiz_number": quiz_number},
            {"$set": {f"questions.{question_number}.answer": answers}}
        )

        if update_result.modified_count == 1:
            return await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        else:
            raise HTTPException(status_code=400, detail="Failed to update answers")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/course/{course_id}/quiz/{quiz_number}/question/{question_number}", response_model=Quiz)
async def update_quiz_question(
        course_id: int,
        quiz_number: int,
        question_number: int,
        question_update: dict
):
    try:
        # Check if quiz exists
        existing_quiz = await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        if not existing_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Check if the question_number is valid
        if question_number < 0 or question_number >= len(existing_quiz["questions"]):
            raise HTTPException(status_code=400, detail="Invalid question number")

        # Update the specific question
        update_result = await quiz_collection.update_one(
            {"course_id": course_id, "quiz_number": quiz_number},
            {"$set": {f"questions.{question_number}": question_update}}
        )

        if update_result.modified_count == 1:
            return await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        else:
            raise HTTPException(status_code=400, detail="Failed to update question")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/course/{course_id}/number/{quiz_number}")
async def delete_quiz(course_id: int, quiz_number: int):
    try:
        quiz_to_delete = await quiz_collection.find_one({"course_id": course_id, "quiz_number": quiz_number})
        if not quiz_to_delete:
            raise HTTPException(status_code=404, detail="Quiz not found")
        delete_result = await quiz_collection.delete_one({"course_id": course_id, "quiz_number": quiz_number})
        await quiz_collection.update_many({"course_id": course_id, "quiz_number": {"$gt": quiz_number}},
                                          {"$inc": {"quiz_number": -1}})
        if delete_result.deleted_count == 1:
            return {"detail": "Quiz successfully deleted"}
        raise HTTPException(status_code=404, detail="Quiz not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid quiz ID")


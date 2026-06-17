import '../../domain/entities/task.dart';
import '../dtos/task_dto.dart';

/// The translation seam between the API world (DTO) and the business
/// world (Entity). Keeps API field names and formats out of the domain.
extension TaskDtoMapper on TaskDto {
  Task toEntity() => Task(
        id: id,
        title: title,
        description: description,
        isDone: completed,
        dueDate: dueDate == null ? null : DateTime.tryParse(dueDate!),
      );
}

extension TaskEntityMapper on Task {
  TaskDto toDto() => TaskDto(
        id: id,
        title: title,
        description: description,
        completed: isDone,
        dueDate: dueDate?.toIso8601String(),
      );
}

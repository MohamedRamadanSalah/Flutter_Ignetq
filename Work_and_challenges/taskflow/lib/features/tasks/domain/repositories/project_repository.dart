import 'package:fpdart/fpdart.dart';
import 'package:taskflow/core/error/failures.dart';
import 'package:taskflow/features/tasks/domain/entities/project.dart';

abstract interface class ProjectRepository {
  Future<Either<Failure, List<Project>>> getProjects({String? cursor});
}
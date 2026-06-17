import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/task_remote_datasource.dart';
import '../../data/repositories/task_repository_impl.dart';
import '../../domain/entities/task.dart';
import '../../domain/repositories/task_repository.dart';
import '../../domain/usecases/get_tasks.dart';

/// ---------------------------------------------------------------------------
/// Dependency wiring (Day 1 skeleton, manual providers).
/// On Day 8 you migrate these to code-gen `@riverpod` functions.
/// Read top-to-bottom: each provider depends on the one above it.
/// ---------------------------------------------------------------------------

final dioProvider = Provider<Dio>((ref) => buildDio());

final taskRemoteDataSourceProvider = Provider<TaskRemoteDataSource>((ref) {
  return TaskRemoteDataSourceImpl(ref.watch(dioProvider));
});

final taskRepositoryProvider = Provider<TaskRepository>((ref) {
  return TaskRepositoryImpl(ref.watch(taskRemoteDataSourceProvider));
});

final getTasksProvider = Provider<GetTasks>((ref) {
  return GetTasks(ref.watch(taskRepositoryProvider));
});

/// First real screen-facing provider. Day 9 replaces this with an
/// `AsyncNotifier` that also supports refresh / create / optimistic updates.
final tasksProvider = FutureProvider<List<Task>>((ref) async {
  final result = await ref.watch(getTasksProvider)(const GetTasksParams());
  // `fold` turns Either into a value or throws — AsyncValue captures the error.
  return result.fold((failure) => throw Exception(failure.message), (t) => t);
});

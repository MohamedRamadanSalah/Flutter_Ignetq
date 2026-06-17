import 'package:fpdart/fpdart.dart';
import '../error/failures.dart';

/// Base contract for every use case (interactor) in the Domain layer.
/// [Type] is what the use case returns on success; [Params] is its input.
///
/// Returns `Either<Failure, Type>`: Left = failure, Right = success.
abstract interface class UseCase<Type, Params> {
  Future<Either<Failure, Type>> call(Params params);
}

/// Use when a use case takes no parameters.
class NoParams {
  const NoParams();
}

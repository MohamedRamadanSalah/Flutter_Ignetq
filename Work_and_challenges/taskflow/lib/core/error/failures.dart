import 'package:equatable/equatable.dart';

/// Domain-level error type. The UI/State layer only ever sees a [Failure],
/// never a raw exception. Data-layer exceptions are mapped to these.
sealed class Failure extends Equatable {
  const Failure(this.message);
  final String message;

  @override
  List<Object?> get props => [message];
}

class ServerFailure extends Failure {
  const ServerFailure([super.message = 'Something went wrong on the server.']);
}

class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'No internet connection.']);
}

class CacheFailure extends Failure {
  const CacheFailure([super.message = 'Could not read local data.']);
}

class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure([super.message = 'Your session has expired.']);
}

class ValidationFailure extends Failure {
  const ValidationFailure(super.message);
}

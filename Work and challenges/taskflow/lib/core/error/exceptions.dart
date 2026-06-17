/// Raw, layer-internal errors thrown by data sources.
/// These NEVER cross into the domain/presentation layers — the repository
/// catches them and maps them to a [Failure].
class ServerException implements Exception {
  ServerException([this.message = 'Server error']);
  final String message;
}

class NetworkException implements Exception {
  NetworkException([this.message = 'Network error']);
  final String message;
}

class CacheException implements Exception {
  CacheException([this.message = 'Cache error']);
  final String message;
}

class UnauthorizedException implements Exception {
  UnauthorizedException([this.message = 'Unauthorized']);
  final String message;
}

#pragma once

// From https://github.com/paboyle/Grid/blob/develop/Grid/threads/Accelerator.h
// Orignal author: Peter Boyle <paboyle@ph.ed.ac.uk>

#include <qlat-utils/qacc.h>
#include <qlat-utils/timer.h>

namespace qlat
{  //

API inline int& qacc_num_threads()
// qlat parameter
{
  static int nt = get_env_long_default("q_acc_num_threads", 32);
  return nt;
}

#define qfor(iter1, num, ...)                    \
  {                                              \
    for (qlat::Long iter1 = 0; iter1 < num; ++iter1) { \
      {__VA_ARGS__};                             \
    }                                            \
  }

#define qfor2d(iter1, num1, iter2, num2, ...)       \
  {                                                 \
    for (qlat::Long iter1 = 0; iter1 < num1; ++iter1) {   \
      for (qlat::Long iter2 = 0; iter2 < num2; ++iter2) { \
        {__VA_ARGS__};                              \
      }                                             \
    }                                               \
  }

#define q_do_pragma(x) _Pragma(#x)

#define qthread_for(iter1, num, ...)             \
  {                                              \
  q_do_pragma(omp parallel for schedule(static)) \
  for (qlat::Long iter1 = 0; iter1 < num; ++iter1)     \
    {                                            \
      {__VA_ARGS__};                             \
    }                                            \
  }

#define qthread_for2d(iter1, num1, iter2, num2, ...) \
  {                                                  \
  q_do_pragma(omp parallel for collapse(2))           \
  for (qlat::Long iter1 = 0; iter1 < num1; ++iter1)        \
    {                                                \
      for (qlat::Long iter2 = 0; iter2 < num2; ++iter2) {  \
        {__VA_ARGS__};                               \
      }                                              \
    }                                                \
  }

#ifdef QLAT_USE_ACC

#ifndef __CUDACC_EXTENDED_LAMBDA__
#error "please compile with --expt-extended-lambda"
#endif

#define qacc_continue return

#define qacc_for2dNB(iter1, num1, iter2, num2, ...)                           \
  {                                                                           \
    if ((num1 != 0) and (num2 != 0)) {                                        \
      typedef qlat::Long QACC_FOR_LOOP_ITERATOR;                                    \
      auto QACC_FOR_LOOP_LAMBDA = [=] __host__ __device__(                    \
                                      QACC_FOR_LOOP_ITERATOR iter1,           \
                                      QACC_FOR_LOOP_ITERATOR iter2) mutable { \
        {__VA_ARGS__};                                                        \
      };                                                                      \
      const int QACC_NUM_THREADS = qlat::qacc_num_threads();                  \
      dim3 CUDA_THREADS_DIM3(QACC_NUM_THREADS, 1, 1);                         \
      dim3 CUDA_BLOCKS_DIM3((num1 + QACC_NUM_THREADS - 1) / QACC_NUM_THREADS, \
                            num2, 1);                                         \
      qacc_Error CUDA_LAST_ERROR_OBJECT = qacc_GetLastError();                \
      if (qacc_Success != CUDA_LAST_ERROR_OBJECT) {                           \
        qerr(qlat::ssprintf("qacc_for: Cuda error %s from '%s' Line %d.",     \
                            qacc_GetErrorString(CUDA_LAST_ERROR_OBJECT),      \
                            __FILE__, __LINE__));                             \
      }                                                                       \
      qlambda_apply<<<CUDA_BLOCKS_DIM3, CUDA_THREADS_DIM3>>>(                 \
          num1, num2, QACC_FOR_LOOP_LAMBDA);                                  \
    }                                                                         \
  }

template <typename Lambda>
__global__ void qlambda_apply(Long num1, Long num2, Lambda lam)
{
  Long x = threadIdx.x + blockDim.x * blockIdx.x;
  Long y = threadIdx.y + blockDim.y * blockIdx.y;
  if ((x < num1) && (y < num2)) {
    lam(x, y);
  }
}

#define qacc_barrier(dummy)                                                \
  {                                                                        \
    qacc_DeviceSynchronize();                                               \
    qacc_Error err = qacc_GetLastError();                                    \
    if (qacc_Success != err) {                                              \
      qlat::displayln(                                                     \
          qlat::ssprintf("qacc_barrier: Cuda error %s from '%s' Line %d.", \
                         qacc_GetErrorString(err), __FILE__, __LINE__));    \
      qassert(false);                                                      \
    }                                                                      \
  }

#define qacc_forNB(iter1, num1, ...) \
  qacc_for2dNB(iter1, num1, iter2, 1, {__VA_ARGS__});

#define qacc_for(iter, num, ...) \
  qacc_forNB(iter, num, {__VA_ARGS__}) qacc_barrier(dummy)

#define qacc_for2d(iter1, num1, iter2, num2, ...) \
  qacc_for2dNB(iter1, num1, iter2, num2, {__VA_ARGS__}) qacc_barrier(dummy)

#else

#define qacc_continue continue

#define qacc_for2dNB(iter1, num1, iter2, num2, ...) \
  qthread_for2d(iter1, num1, iter2, num2, {__VA_ARGS__})

#define qacc_forNB(iter1, num1, ...) qthread_for(iter1, num1, {__VA_ARGS__})

#define qacc_barrier(dummy)

#define qacc_for2d(iter1, num1, iter2, num2, ...) \
  qacc_for2dNB(iter1, num1, iter2, num2, {__VA_ARGS__}) qacc_barrier(dummy)

#define qacc_for(iter, num, ...) \
  qacc_forNB(iter, num, {__VA_ARGS__}) qacc_barrier(dummy);

#endif

}  // namespace qlat

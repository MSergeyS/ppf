function  [ parameters ] = packag_CC_mode5( parameters )

%**************************************************************************  
% упаковка сигнала в команды управления генератор DDS5, версия v5
% режим работы 2
% -------------------------------------------------------------------------
% Входные данные:
%     - parameters    - параметры ЗИ
%
% Выходные данные:
%     - parameters    - параметры ЗИ
% 
%**************************************************************************
%
%**************************************************************************
% 
% Мосолов С.
% v 1.0: 13 September 2017


  try

    % инициализация
    str_CC{1} = '-------------------------------------------------------------------------------------';
    str_CC{2} = 'номер СС | Polarity |   T |  sum(T) |  CC ';
    str_CC{3} = '-------------------------------------------------------------------------------------';    
    NumTic = 0;
    CC = [];
    indexCC = 0;

    for k = 0:numel(parameters.index_Z)
        
       % длительность интервала
       if k == 0    % первый интервал
           T = parameters.index_Z(1)-1;
       elseif k <= numel(parameters.index_Z)-1
           T = parameters.index_Z(k+1) - parameters.index_Z(k);
       else         % последний интервал
           T = numel(parameters.signal_packaging) - parameters.index_Z(k);
           if T < 2
               continue
           end
       end
      
       % импульс
       if (k~=0) && (parameters.signal_packaging(parameters.index_Z(k)) == 1)
           Polarity = 1;    % положительный импульс
           maxT = 2^8 - 2 + 2;
       elseif (k~=0) && (parameters.signal_packaging(parameters.index_Z(k)) == -1)
           Polarity = -1;   % отрицательный импульс
           maxT = 2^8 - 1 + 2;
       else
           Polarity = 0;    % пауза
           maxT = 2^9 - 2 + 2;
       end

       nr = fix((T)/maxT);
       T = rem(T,maxT);
       if (nr == 0)  
           [ indexCC, CC, str_CC, NumTic ] = ...
                         form_CC(indexCC, T, Polarity, CC, str_CC, NumTic);
       else    % Длительность интервала больше maxT
           for j = 1:nr
              [ indexCC, CC, str_CC, NumTic ] = ...
                      form_CC(indexCC, maxT, Polarity, CC, str_CC, NumTic);
              [ indexCC, CC, str_CC, NumTic ] = ...
                                form_CC(indexCC, 0, 0, CC, str_CC, NumTic);
           end
           [ indexCC, CC, str_CC, NumTic ] = ...
                         form_CC(indexCC, T, Polarity, CC, str_CC, NumTic);
       end
       
       if rem(indexCC,2) && Polarity ~= 0
           dm_log('   Ошибка!!!')
       end

    end

    parameters.timeZI = NumTic*parameters.Tclk;
    
    % признак конца (последняя КУ) ----------------------------------------
    % конец - если все единицы
        indexCC = indexCC + 1;
        T = 2^8-1;
        CC_actual = uint16(T);
        CC_actual = bitset(CC_actual,9,'uint16');
        CC = [CC CC_actual];
        Polarity = 1;
        tmp_str = sprintf('% 8u | % 8i | % 3u |         | %04Xh', ...
                          indexCC, ...
                          Polarity, ...
                          T, ...
                          CC_actual);
        str_CC = [str_CC tmp_str];
    %----------------------------------------------------------------------

    str_CC{numel(str_CC)+1} = ...
        '----------------------------------------------------------------';
    str_CC{numel(str_CC)+1} = ...
        ['                           Tзи = ',num2str(1e6*parameters.timeZI,'%6.3f'),' мкс']; 

    parameters.CC = CC;
    parameters.str_CC = str_CC;
   
  catch err
    rethrow(err);
  end 
end

function [ indexCC, CC, str_CC, NumTic ] = form_CC(indexCC, T, Polarity, CC, str_CC, NumTic)
   indexCC = indexCC + 1;
   CC_actual = uint16(T-2);
   if Polarity == -1
      CC_actual = bitset(CC_actual,9,'uint16');
   end
   CC = [CC CC_actual];
   if T > 0
       NumTic = NumTic + T;
   end
   tmp_str = sprintf('% 8u | % 8i | % 3u | % 7u | %04Xh', ...
                      indexCC, ...
                      Polarity, ...
                      T, ...
                      NumTic, ...
                      CC_actual);
   str_CC = [str_CC tmp_str];
end